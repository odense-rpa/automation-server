import subprocess
import os
import tempfile
import shutil
import logging
from contextlib import contextmanager

logger = logging.getLogger(__name__)


def remove_readonly(func, path, excinfo):
    os.chmod(path, 0o777)
    func(path)

@contextmanager
def temporary_directory():
    dirpath = tempfile.mkdtemp()
    try:
        yield dirpath
    finally:
        shutil.rmtree(dirpath, onerror=remove_readonly)


def run_command(command, cwd=None, env=None):
    result = subprocess.run(
        command, shell=True, cwd=cwd, env=env, capture_output=True, text=True
    )
    return result.stdout, result.stderr, result.returncode


def get_venv_python(venv_path):
    if os.name == "nt":  # Windows
        return os.path.join(venv_path, "Scripts", "python.exe")
    else:  # Unix-based systems
        return os.path.join(venv_path, "bin", "python")


def get_venv_pip(venv_path):
    if os.name == "nt":  # Windows
        return os.path.join(venv_path, "Scripts", "pip.exe")
    else:  # Unix-based systems
        return os.path.join(venv_path, "bin", "pip")


def run_python(repo_url, pat, environment=None):
    with temporary_directory() as temp_dir:
        # Step 1: Clone the GitHub repository
        clone_url = (
            repo_url if pat is None else repo_url.replace("https://", f"https://{pat}@")
        )
        clone_command = f"git clone {clone_url} {temp_dir}"

        logger.info(f"Cloning repository: {repo_url}")
        stdout, stderr, returncode = run_command(clone_command)

        if returncode != 0:
            logger.error(f"Failed to clone repository. Return code: {returncode}")
            logger.error(f"{stderr}")

        # Step 2: Set up virtual environment
        venv_path = os.path.join(temp_dir, ".venv")
        venv_command = f"python -m venv {venv_path}"

        logger.info(f"Creating virtual environment: {venv_path}")

        stdout, stderr, returncode = run_command(venv_command)

        logger.info(f"Venv creation stdout: {stdout}")

        if returncode != 0:
            logger.error(f"Venv creation stderr: {stderr}")

        # Step 3: Install requirements if present
        requirements_path = os.path.join(temp_dir, "requirements.txt")
        if os.path.exists(requirements_path):
            pip_install_command = (
                f"{get_venv_pip(venv_path)} install -r requirements.txt"
            )
            logger.info(f"Installing dependencies: {pip_install_command}")
            stdout, stderr, returncode = run_command(
                pip_install_command, cwd=temp_dir
            )
            #logger.info(f"Pip install stdout: {stdout}")
            if returncode != 0:
                logger.error(f"Pip install stderr: {stderr}")
        else:
            logger.info("No requirements.txt found, skipping dependency installation.")

        # Step 4: Find and execute main.py or app.py
        script_to_run = None
        if os.path.exists(os.path.join(temp_dir, "main.py")):
            script_to_run = "main.py"
        elif os.path.exists(os.path.join(temp_dir, "app.py")):
            script_to_run = "app.py"

        if script_to_run:
            
            # Get current environment and append custom variables
            current_env = os.environ.copy()
            if environment:
                current_env.update(environment)
                  
            
            
            run_script_command = f"{get_venv_python(venv_path)} {script_to_run}"
            logger.info(f"Running script: {run_script_command}")
            stdout, stderr, returncode = run_command(
                run_script_command, cwd=temp_dir, env=current_env
            )
            
            if returncode == 0:
                logger.info(f"Script execution successful. return code: {returncode}")

            if returncode != 0 and stderr:
                logger.error(f"Script execution stderr: {stderr}")

                raise RuntimeError(f"Script execution failed. Return code: {returncode}")
    
        else:
            logger.warning("No main.py or app.py found to execute.")