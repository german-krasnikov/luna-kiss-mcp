"""Version tracking mixin for LessonStore — typemap_versions table operations."""
from __future__ import annotations

import time
from typing import Optional


class VersionStoreMixin:
    """Mixin that adds typemap_versions table management to a SQLite-backed store.

    Expects self._conn (sqlite3.Connection) and self._lock (threading.Lock).
    """

    _FIRST_SEEN = object()  # sentinel: class not previously seen

    def ensure_versions_table(self) -> None:
        with self._lock:
            self._conn.execute("""
                CREATE TABLE IF NOT EXISTS typemap_versions (
                    class_hash TEXT PRIMARY KEY,
                    sig_hash TEXT NOT NULL,
                    typemap_version TEXT NOT NULL,
                    seen_at REAL NOT NULL
                )
            """)
            self._conn.commit()

    def get_version(self, class_hash: str) -> Optional[dict]:
        with self._lock:
            cur = self._conn.execute(
                "SELECT sig_hash, typemap_version FROM typemap_versions WHERE class_hash=?",
                (class_hash,),
            )
            row = cur.fetchone()
        if row is None:
            return None
        return {"sig_hash": row[0], "typemap_version": row[1]}

    def upsert_version(self, class_hash: str, sig_hash: str, typemap_version: str) -> None:
        with self._lock:
            self._conn.execute(
                "INSERT OR REPLACE INTO typemap_versions VALUES(?, ?, ?, ?)",
                (class_hash, sig_hash, typemap_version, time.time()),
            )
            self._conn.commit()

    def swap_version_if_changed(self, class_hash: str, new_sig: str, version: str):
        """Atomically check old sig and update to new sig.

        Returns:
          VersionStoreMixin._FIRST_SEEN  — no prior record (first sighting)
          None                           — same sig, no change
          str (old_sig_hash)             — sig drifted, returns previous hash
        """
        with self._lock:
            cur = self._conn.execute(
                "SELECT sig_hash FROM typemap_versions WHERE class_hash=?", (class_hash,)
            )
            row = cur.fetchone()
            old_sig = row[0] if row else None
            self._conn.execute(
                "INSERT OR REPLACE INTO typemap_versions VALUES(?, ?, ?, ?)",
                (class_hash, new_sig, version, time.time()),
            )
            self._conn.commit()
        if old_sig is None:
            return VersionStoreMixin._FIRST_SEEN
        return old_sig if old_sig != new_sig else None
