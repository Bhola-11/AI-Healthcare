"""
HealthSphere Metrics & Integrity Verification Script.
Tracks LOC, Commit counts, PR milestones, and code health.
"""
import os
import subprocess
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

VALID_EXTENSIONS = {
    '.py': 'Python',
    '.html': 'Django Templates / HTML',
    '.css': 'CSS3 / Stylesheets',
    '.js': 'JavaScript / ES6',
    '.json': 'JSON / Data Fixtures',
    '.sql': 'SQL DDL / Schema',
    '.md': 'Markdown / Documentation',
    '.yml': 'YAML / CI Configs',
    '.yaml': 'YAML / CI Configs',
    '.sh': 'Shell / Bash Scripts',
}

EXCLUDE_DIRS = {
    '.git',
    '__pycache__',
    'venv',
    'env',
    '.venv',
    'staticfiles',
    'node_modules',
    '.idea',
    '.vscode',
}

def count_loc():
    metrics = {lang: {'files': 0, 'lines': 0, 'blank': 0, 'comment': 0, 'code': 0} for lang in set(VALID_EXTENSIONS.values())}
    total_files = 0
    total_lines = 0

    for root, dirs, files in os.walk(BASE_DIR):
        dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS and not d.startswith('.')]
        for file in files:
            ext = os.path.splitext(file)[1].lower()
            if ext in VALID_EXTENSIONS:
                filepath = os.path.join(root, file)
                lang = VALID_EXTENSIONS[ext]
                try:
                    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                        lines = f.readlines()
                    line_count = len(lines)
                    blank_count = sum(1 for l in lines if not l.strip())
                    code_count = line_count - blank_count
                    
                    metrics[lang]['files'] += 1
                    metrics[lang]['lines'] += line_count
                    metrics[lang]['blank'] += blank_count
                    metrics[lang]['code'] += code_count
                    total_files += 1
                    total_lines += line_count
                except Exception as e:
                    pass

    return metrics, total_files, total_lines

def get_git_commit_count():
    try:
        res = subprocess.run(['git', 'rev-list', '--count', 'HEAD'], cwd=BASE_DIR, capture_output=True, text=True, check=True)
        return int(res.stdout.strip())
    except Exception:
        return 0

def get_git_branches():
    try:
        res = subprocess.run(['git', 'branch', '-a'], cwd=BASE_DIR, capture_output=True, text=True, check=True)
        branches = [b.strip().replace('* ', '') for b in res.stdout.splitlines() if b.strip()]
        return branches
    except Exception:
        return []

def main():
    print("=" * 70)
    print("        HEALTHSPHERE PLATFORM METRICS VERIFICATION REPORT")
    print("=" * 70)
    
    commit_count = get_git_commit_count()
    branches = get_git_branches()
    pr_branches = [b for b in branches if 'pr/' in b]
    
    metrics, total_files, total_lines = count_loc()
    
    print(f"\n[GIT STATUS]")
    print(f"Total Git Commits: {commit_count} / Target: 120")
    print(f"Total PR Branches tracked: {len(pr_branches)} / Target: 100")
    
    print(f"\n[LINES OF CODE (LOC) BREAKDOWN]")
    print(f"{'Language / Category':<30} | {'Files':<8} | {'Total LOC':<12} | {'Code LOC':<10}")
    print("-" * 70)
    total_code_loc = 0
    for lang, data in sorted(metrics.items(), key=lambda x: x[1]['lines'], reverse=True):
        if data['files'] > 0:
            print(f"{lang:<30} | {data['files']:<8} | {data['lines']:<12} | {data['code']:<10}")
            total_code_loc += data['code']
    print("-" * 70)
    print(f"{'TOTAL ACROSS ALL MODULES':<30} | {total_files:<8} | {total_lines:<12} | {total_code_loc:<10}")
    print("=" * 70)

if __name__ == '__main__':
    main()
