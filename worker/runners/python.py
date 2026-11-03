"""Runs a Python automation: clone the repo, prepare its environment, run main.py.

Logging is aimed at the operator: one line per phase, command output only when
something fails (and then only the tail), exact commands at DEBUG level.
"""

import fcntl
import logging
import os
import shlex
import signal
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from typing import Dict, Optional

import git

from errors import SessionError

logger = logging.getLogger(__name__)

TAIL_LINES = 20
TAIL_CHARS = 4000


def tail(text: str, workdir: Optional[Path] = None) -> str:
    """Last lines of command output, bounded in size, with temp paths shortened."""
    if workdir is not None:
        text = text.replace(str(workdir), "<repo>")
    lines = text.strip().splitlines()[-TAIL_LINES:]
    return "\n".join(lines)[-TAIL_CHARS:]


def describe_exit(returncode: int) -> str:
    """Operator-facing exit description; a negative code means killed by a signal."""
    if returncode < 0:
        try:
            name = signal.Signals(-returncode).name
        except ValueError:
            name = "unknown signal"
        return f"was killed by signal {-returncode} ({name})"
    return f"failed with exit code {returncode}"


def run_command(
    args: list, cwd: Path, env: Optional[dict] = None
) -> subprocess.CompletedProcess:
    """Run a command without a shell and capture its output."""
    logger.debug("Executing: %s (cwd=%s)", shlex.join(map(str, args)), cwd)
    return subprocess.run(
        [str(a) for a in args],
        cwd=cwd,
        env={**os.environ, **(env or {})},
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )


def run_step(name: str, args: list, cwd: Path) -> None:
    """Run a preparation step; raise SessionError with the output tail on failure."""
    result = run_command(args, cwd)
    if result.returncode != 0:
        output = tail(result.stderr or result.stdout, cwd)
        raise SessionError(
            f"{name} {describe_exit(result.returncode)}"
            + (f":\n{output}" if output else "")
        )


def venv_bin(venv_path: Path, name: str) -> Path:
    if sys.platform == "win32":
        return venv_path / "Scripts" / f"{name}.exe"
    return venv_path / "bin" / name


def run_python(
    repo_url: str,
    username: Optional[str] = None,
    token: Optional[str] = None,
    script_env: Optional[Dict[str, str]] = None,
    parameters: Optional[str] = None,
    git_options: Optional[str] = None,
) -> None:
    """Clone the repo, set up its environment with uv and run main.py.

    Args:
        repo_url: Git repository URL.
        username: Git username for authentication (if needed).
        token: Personal access token for authentication (if needed).
        script_env: Environment variables passed to main.py.
        parameters: Command-line parameters for main.py, split like a shell
            would (quotes respected, no variable expansion).
        git_options: Extra arguments for `git clone`, e.g. "--branch=dev".

    Raises:
        SessionError: with an operator-facing message if any phase fails.
    """
    try:
        clone_options = ["--recurse-submodules"] + shlex.split(git_options or "")
        script_args = shlex.split(parameters or "")
    except ValueError as e:
        raise SessionError(f"Invalid git options or parameters: {e}") from None

    with tempfile.TemporaryDirectory() as temp_dir:
        workdir = Path(temp_dir)
        started = time.monotonic()

        clone_url = repo_url
        if username and token:
            clone_url = repo_url.replace("https://", f"https://{username}:{token}@")
        try:
            git.Repo.clone_from(clone_url, workdir, multi_options=clone_options)
        except git.exc.GitCommandError as e:
            message = str(e).replace(token, "***") if token else str(e)
            raise SessionError(f"Cloning {repo_url} failed:\n{tail(message)}") from None

        venv_path = workdir / ".venv"
        python = venv_bin(venv_path, "python")
        prepared = []

        run_step("Creating virtual environment", ["uv", "venv", venv_path], workdir)
        if (workdir / "requirements.txt").exists():
            run_step("Installing pip", [python, "-m", "ensurepip"], workdir)
            run_step(
                "Installing dependencies (requirements.txt)",
                [python, "-m", "pip", "install", "-r", "requirements.txt"],
                workdir,
            )
            prepared.append("requirements.txt")
        elif (workdir / "pyproject.toml").exists():
            run_step(
                "Installing dependencies (uv sync)",
                ["uv", "sync", "--refresh"],
                workdir,
            )
            prepared.append("uv sync")
        else:
            prepared.append("no dependencies")

        playwright = venv_bin(venv_path, "playwright")
        if playwright.exists():
            browsers = Path(os.environ.get("PLAYWRIGHT_BROWSERS_PATH", "/tmp"))
            with open(browsers / ".install.lock", "w") as lock_file:
                fcntl.flock(lock_file, fcntl.LOCK_EX)
                try:
                    run_step(
                        "Installing Playwright browsers",
                        [playwright, "install", "chromium"],
                        workdir,
                    )
                finally:
                    fcntl.flock(lock_file, fcntl.LOCK_UN)
            prepared.append("Playwright chromium")

        main_script = workdir / "main.py"
        if not main_script.exists():
            raise SessionError("main.py not found in the repository")

        logger.info(
            "Environment ready in %.1fs (%s)",
            time.monotonic() - started,
            ", ".join(prepared),
        )

        started = time.monotonic()
        result = run_command([python, main_script, *script_args], workdir, script_env)
        duration = time.monotonic() - started

        if result.returncode != 0:
            output = tail(result.stderr or result.stdout, workdir)
            raise SessionError(
                f"main.py {describe_exit(result.returncode)} after {duration:.1f}s"
                + (f". Last lines of output:\n{output}" if output else "")
            )
        logger.info("main.py finished in %.1fs", duration)
