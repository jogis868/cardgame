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
    run([PYTHON, "-m", "venv", VENV_DIR])

if os.name == "nt":
    pip_path = os.path.join(VENV_DIR, "Scripts", "pip.exe")
    python_path = os.path.join(VENV_DIR, "Scripts", "python.exe")
    # If pip is missing, install it manually
    if not os.path.isfile(pip_path):
        run([python_path, "get-pip.py"])

# 2) install/update pip and project requirements
if os.name == "nt":
    PIP = os.path.join(VENV_DIR, "Scripts", "pip.exe")
    PY = os.path.join(VENV_DIR, "Scripts", "python.exe")
else:
    PIP = os.path.join(VENV_DIR, "bin", "pip")
    PY = os.path.join(VENV_DIR, "bin", "python")

run([PIP, "install", "--upgrade", "pip"])
run([PIP, "install", "-r", "requirements.txt"])

# 3) run Django
run([PY, "manage.py", "runserver"])
