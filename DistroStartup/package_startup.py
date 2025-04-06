#!/ryler/bin/env python3

import subprocess
import os
import time
from pathlib import Path

ROOT_PATH = Path(__file__).resolve().parent

def create_environment():
    if not os.path.exists(".venv"):
        venv = subprocess.check_call(["python3", "-m", "venv", ".venv"])

def install_dependencies():
    pip_path = str(ROOT_PATH) + "/.venv/bin/pip"
    requirement_path = str(ROOT_PATH) + "/requirements.txt"
    subprocess.check_call([pip_path, "install", "-r", requirement_path])

def run_script():
    python_path = str(ROOT_PATH) + "/.venv/bin/python3"
    script_path = str(ROOT_PATH) + "/starter.py"
    subprocess.Popen([python_path, script_path])

if __name__ == "__main__":
    create_environment()
    install_dependencies()
    run_script()