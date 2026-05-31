"""SessionHistory: SQLite-backed per-project session storage."""
from __future__ import annotations

import hashlib
import os
import pathlib
import sqlite3
import threading
from dataclasses import dataclass


@dataclass
class SessionRow:
    ts: float
    project_key: str
    total_spent: int
    cap: int
    skipped: int
    downgraded: int
    hit_cap: int   # 1 if spent >= cap
    success: int   # 1 if spent < cap*0.95


def get_project_key() -> str:
    """Stable 12-char hex key per project."""
    explicit = os.environ.get("LUNA_PROJECT")
    src = explicit if explicit else os.getcwd()
    return hashlib.sha256(src.encode()).hexdigest()[:12]


class SessionHistory:
    def __init__(self, db_path: pathlib.Path):
        self._lock = threading.Lock()
        db_path.parent.mkdir(parents=True, exist_ok=True)
        self._conn = sqlite3.connect(str(db_path), check_same_thread=False, timeout=1.0)
        self._conn.execute("PRAGMA journal_mode=WAL")
        self._conn.execute("""
            CREATE TABLE IF NOT EXISTS sessions (
                id INTEGER PRIMARY KEY,
                ts REAL NOT NULL,
                project_key TEXT NOT NULL,
                total_spent INTEGER NOT NULL,
                cap INTEGER NOT NULL,
                skipped INTEGER DEFAULT 0,
                downgraded INTEGER DEFAULT 0,
                hit_cap INTEGER DEFAULT 0,
                success INTEGER DEFAULT 1
            )""")
        self._conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_proj_ts ON sessions(project_key, ts DESC)"
        )
        self._conn.commit()

    def record(self, row: SessionRow) -> None:
        with self._lock:
            self._conn.execute(
                "INSERT INTO sessions(ts,project_key,total_spent,cap,skipped,downgraded,hit_cap,success)"
                " VALUES(?,?,?,?,?,?,?,?)",
                (row.ts, row.project_key, row.total_spent, row.cap,
                 row.skipped, row.downgraded, row.hit_cap, row.success),
            )
            self._conn.commit()

    def recent(self, project_key: str, limit: int = 30) -> list[SessionRow]:
        with self._lock:
            cur = self._conn.execute(
                "SELECT ts,project_key,total_spent,cap,skipped,downgraded,hit_cap,success"
                " FROM sessions WHERE project_key=? ORDER BY ts DESC LIMIT ?",
                (project_key, limit),
            )
            return [SessionRow(*r) for r in cur.fetchall()]

    def close(self) -> None:
        self._conn.close()
