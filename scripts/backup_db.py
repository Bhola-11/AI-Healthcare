import os
import shutil
import sqlite3
from datetime import datetime
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "db.sqlite3"
BACKUP_DIR = BASE_DIR / "backups"

def backup_sqlite_wal():
    BACKUP_DIR.mkdir(exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    target_backup = BACKUP_DIR / f"healthsphere_backup_{timestamp}.sqlite3"
    
    print(f"Connecting to source database: {DB_PATH}")
    src_conn = sqlite3.connect(DB_PATH)
    dst_conn = sqlite3.connect(target_backup)
    
    with dst_conn:
        src_conn.backup(dst_conn, pages=100)
        
    dst_conn.close()
    src_conn.close()
    print(f"Successfully performed online SQLite WAL backup to: {target_backup}")

if __name__ == '__main__':
    backup_sqlite_wal()
