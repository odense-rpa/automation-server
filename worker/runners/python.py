import subprocess
import os
import tempfile
import logging
import sys

from pathlib import Path
from typing import Optional, Tuple, Dict, List

import git


logger = logging.getLogger(__name__)


def run_command(
    cmd: str, cwd: Optional[str] = None, env: Optional[dict] = None
) -> Tuple[str, str, int]:
    """Runs a shell command with logging and error handling.

    Returns:
        Tuple containing:
        - stdout (str): The standard output of the command.
        - stderr (str): The standard error of the command.
        - returncode (int): Exit code of the command (0 = success, non-zero = failure).
    """
    merged_env = os.environ.copy()
    if env:
        merged_env.update(env)

    logging.info(f"Executing: {cmd} (cwd={cwd})")

    result = subprocess.run(
        cmd,
        shell=True,
        cwd=cwd,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env=merged_env,
        encoding="utf-8",
    )
    # Log outputs
    if result.stdout:
        logging.info(f"STDOUT:\n{result.stdout.strip()}")
    if result.stderr and result.returncode != 0:
        logging.error(f"STDOUT:\n{result.stdout.strip()}")
        logging.error(f"STDERR:\n{result.stderr.strip()}")

    return result.stdout, result.stderr, result.returncode


def get_python_executable(venv_path) -> str:
    """Determine the correct Python executable path in the virtual environment."""
    return venv_path / (
        "Scripts/python.exe" if sys.platform == "win32" else "bin/python"
    )


def run_python(
    repo_url: str,
    username: Optional[str] = None,
    token: Optional[str] = None,
    script_env: Optional[Dict[str, str]] = None,
    script_args: Optional[List[str]] = None,
) -> Tuple[Optional[str], Optional[str], int]:
    """Clones repo, sets up env with 'uv', installs deps, and runs main.py.

    Args:
        repo_url (str): Git repository URL.
        username (Optional[str]): Git username for authentication (if needed).
        token (Optional[str]): Personal Access Token for authentication (if needed).
        script_env (Optional[Dict[str, str]]): Environment variables to pass when running main.py.
        script_args (Optional[List[str]]): Command-line arguments to pass to main.py.

    Returns:
        Tuple[str | None, str | None, int]: (stdout, stderr, return code).
    """

    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)

        # Inject authentication into the repo URL if credentials are provided
        if username and token:
            repo_url = repo_url.replace("https://", f"https://{username}:{token}@")

        # Clone the repo
        logging.info(f"Cloning repository into {temp_path}...")
        try:
            git.Repo.clone_from(repo_url, temp_path)
        except git.exc.GitCommandError as e:
            logging.error(f"Git clone failed: {e}")
            return None, None, 1

        # Initialize virtual environment using 'uv'
        venv_path = temp_path / ".venv"
        logging.info("Setting up virtual environment with 'uv'...")
        run_command(f"uv venv {venv_path}", cwd=temp_path)

        # Get the correct Python executable inside .venv
        python_executable = get_python_executable(venv_path)

        # Ensure pip is installed in the correct environment
        logging.info("Ensuring pip is available in the virtual environment...")
        run_command(f"{python_executable} -m ensurepip", cwd=temp_path)

        # Install dependencies
        if (temp_path / "requirements.txt").exists():
            logging.info("Installing dependencies from requirements.txt...")
            run_command(
                f"{python_executable} -m pip install -r requirements.txt", cwd=temp_path
            )
        elif (temp_path / "pyproject.toml").exists():
            logging.info("Installing dependencies using 'uv sync'...")
            run_command("uv sync --refresh", cwd=temp_path)
        else:
            logging.warning(
                "No requirements.txt or pyproject.toml found. Skipping dependency installation."
            )

        # Run the main.py script
        main_script = temp_path / "main.py"
        if main_script.exists():
            logging.info("Running main.py...")

            # Convert script_args list to a space-separated string
            script_args_str = " ".join(script_args) if script_args else ""

            stdout, stderr, returncode = run_command(
                f"{python_executable} {main_script} {script_args_str}",
                cwd=temp_path,
                env=script_env,
            )

            if returncode == 0:
                logging.info("Execution completed successfully.")
            else:
                logging.error(f"Execution failed with return code {returncode}")

            return stdout, stderr, returncode
        else:
            logging.error("Error: main.py not found in the repository.")
            return None, None, 1
