#!/usr/bin/env python3
import os
import sys
import subprocess
import urllib.request

VENV_DIR = "venv"
PYTHON = sys.executable

# Helper to run subprocess commands
def run(cmd, **kw):
    print(f"> {' '.join(cmd)}")
    subprocess.check_call(cmd, **kw)

# 1) create venv if it doesn't exist
if not os.path.isdir(VENV_DIR):
    if os.name == "nt":
        # On Windows, skip pip bootstrapping to avoid ensurepip errors
        run([PYTHON, "-m", "venv", VENV_DIR, "--without-pip"])
    else:
        run([PYTHON, "-m", "venv", VENV_DIR])

# 2) ensure pip is available
if os.name == "nt":
    pip_path = os.path.join(VENV_DIR, "Scripts", "pip.exe")
    python_path = os.path.join(VENV_DIR, "Scripts", "python.exe")
    # If pip is missing, download and install get-pip.py
    if not os.path.isfile(pip_path):
        get_pip = "get-pip.py"
        if not os.path.isfile(get_pip):
            print("Downloading get-pip.py...")
            urllib.request.urlretrieve(
                "https://bootstrap.pypa.io/get-pip.py", get_pip
            )
        run([python_path, get_pip])
else:
    pip_path = os.path.join(VENV_DIR, "bin", "pip")
    python_path = os.path.join(VENV_DIR, "bin", "python")

# 3) install/update pip and project requirements
run([pip_path, "install", "--upgrade", "pip"])
run([pip_path, "install", "-r", "requirements.txt"])

# 4) run Django
run([python_path, "manage.py", "runserver"])
