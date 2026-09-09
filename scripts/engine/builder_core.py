import os
import subprocess
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent.parent
os.chdir(ROOT_DIR)

def run_cmd(cmd, check=True):
    print(f">> {cmd}")
    res = subprocess.run(cmd, shell=True, capture_output=True, text=True, cwd=str(ROOT_DIR))
    if check and res.returncode != 0:
        print(f"FAILED: {res.stderr}")
        sys.exit(1)
    return res

def write_file(rel_path, content):
    full_path = ROOT_DIR / rel_path
    os.makedirs(full_path.parent, exist_ok=True)
    with open(full_path, "w", encoding="utf-8") as f:
        f.write(content)

def pr_branch(name):
    # If branch already exists, switch to it, else create
    res = subprocess.run(f"git rev-parse --verify {name}", shell=True, capture_output=True, cwd=str(ROOT_DIR))
    if res.returncode == 0:
        run_cmd(f"git checkout {name}")
    else:
        run_cmd(f"git checkout -b {name}")

def pr_commit(files, message):
    for f in files:
        run_cmd(f"git add {f}")
    run_cmd(f'git commit -m "{message}"')

def pr_merge(branch_name):
    run_cmd("git checkout main")
    run_cmd(f"git merge {branch_name} --no-edit")
