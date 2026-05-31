"""SQLite store for applied patch history."""
import pathlib
import sqlite3
import threading
import time
from typing import Optional


class PatchStore:
    def __init__(self, db_path: pathlib.Path):
        self._db_path = db_path
        self._lock = threading.Lock()
        db_path.parent.mkdir(parents=True, exist_ok=True)
        self._conn = sqlite3.connect(str(db_path), check_same_thread=False, timeout=1.0)
        self._conn.execute("PRAGMA journal_mode=WAL")
        self._conn.execute("""
            CREATE TABLE IF NOT EXISTS applied_patches (
                patch_id TEXT PRIMARY KEY,
                intent TEXT,
                jakefile_path TEXT,
                shadow_commit_sha TEXT,
                applied_at REAL,
                status TEXT DEFAULT 'applied'
            )
        """)
        self._conn.commit()

    def record(self, patch_id: str, intent: str, jakefile_path: str, sha: str) -> None:
        with self._lock:
            self._conn.execute("""
                INSERT OR REPLACE INTO applied_patches
                (patch_id, intent, jakefile_path, shadow_commit_sha, applied_at, status)
                VALUES (?, ?, ?, ?, ?, 'applied')
            """, (patch_id, intent, jakefile_path, sha, time.time()))
            self._conn.commit()

    def find(self, patch_id: str) -> Optional[dict]:
        with self._lock:
            cur = self._conn.execute(
                "SELECT patch_id, intent, jakefile_path, shadow_commit_sha, applied_at, status "
                "FROM applied_patches WHERE patch_id=?", (patch_id,)
            )
            row = cur.fetchone()
        if row is None:
            return None
        cols = ["patch_id", "intent", "jakefile_path", "shadow_commit_sha", "applied_at", "status"]
        return dict(zip(cols, row))

    def update_status(self, patch_id: str, status: str) -> None:
        with self._lock:
            self._conn.execute(
                "UPDATE applied_patches SET status=? WHERE patch_id=?", (status, patch_id)
            )
            self._conn.commit()

    def close(self) -> None:
        self._conn.close()
