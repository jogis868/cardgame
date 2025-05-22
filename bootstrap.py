#!/usr/bin/env python3
import os
import sys
import subprocess

VENV_DIR = "venv"
PYTHON = sys.executable

def run(cmd, **kw):
    print(f"> {' '.join(cmd)}")
    subprocess.check_call(cmd, **kw)

# 1) create venv if it doesn't exist
if not os.path.isdir(VENV_DIR):
    # On Windows, bypass ensurepip errors by skipping pip bootstrap
    if os.name == "nt":
        run([PYTHON, "-m", "venv", VENV_DIR, "--without-pip"])
    else:
        run([PYTHON, "-m", "venv", VENV_DIR])

# 2) ensure pip is available
if os.name == "nt":
    pip_path = os.path.join(VENV_DIR, "Scripts", "pip.exe")
    python_path = os.path.join(VENV_DIR, "Scripts", "python.exe")
    # If pip is missing, install it manually
    if not os.path.isfile(pip_path):
        # Make sure get-pip.py is in the same directory
        run([python_path, "get-pip.py"])
else:
    pip_path = os.path.join(VENV_DIR, "bin", "pip")
    python_path = os.path.join(VENV_DIR, "bin", "python")

# 3) install/update pip and project requirements
run([pip_path, "install", "--upgrade", "pip"])
run([pip_path, "install", "-r", "requirements.txt"])

# 4) run Django
run([python_path, "manage.py", "runserver"])
