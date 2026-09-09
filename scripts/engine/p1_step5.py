from builder_core import run_cmd, write_file, pr_branch, pr_commit, pr_merge

pr_branch("pr/006-db-optimization")

# Append WAL pragma to base.py if not present
with open("config/settings/base.py", "r", encoding="utf-8") as f:
    content = f.read()

wal_snippet = """
from django.db.backends.signals import connection_created
from django.dispatch import receiver

@receiver(connection_created)
def configure_sqlite_wal(sender, connection, **kwargs):
    if connection.vendor == 'sqlite':
        cursor = connection.cursor()
        cursor.execute('PRAGMA journal_mode = WAL;')
        cursor.execute('PRAGMA synchronous = NORMAL;')
        cursor.execute('PRAGMA foreign_keys = ON;')
        cursor.execute('PRAGMA busy_timeout = 60000;')
"""
if "configure_sqlite_wal" not in content:
    with open("config/settings/base.py", "a", encoding="utf-8") as f:
        f.write(wal_snippet)

run_cmd("python manage.py makemigrations accounts")
run_cmd("python manage.py makemigrations audit")
run_cmd("python manage.py migrate")

pr_commit(["config/settings/base.py", "apps/accounts/migrations/", "apps/audit/migrations/"], "chore(db): configure sqlite wal mode, foreign key pragmas and initial schema migrations")
pr_merge("pr/006-db-optimization")
print("PR 6 merged successfully.")
