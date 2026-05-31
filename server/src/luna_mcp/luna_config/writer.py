"""Atomic write + one-slot backup/revert for config.json."""
from __future__ import annotations

import json
import pathlib
import shutil
import tempfile


def write_config(path: pathlib.Path, data: dict) -> None:
    """Atomically write data to path; keep one .bak slot. Raises TypeError if not dict."""
    if not isinstance(data, dict):
        raise TypeError(f"config data must be a dict, got {type(data).__name__}")
    # Backup existing file
    if path.exists():
        shutil.copy2(path, path.with_suffix(".json.bak"))
    # Atomic write via NamedTemporaryFile (avoids TOCTOU race of mktemp)
    with tempfile.NamedTemporaryFile(
        dir=path.parent, prefix=".cfg_", suffix=".tmp",
        delete=False, mode="w", encoding="utf-8",
    ) as tmp_fh:
        tmp_fh.write(json.dumps(data, indent=2, ensure_ascii=False))
        tmp_path = pathlib.Path(tmp_fh.name)
    try:
        tmp_path.replace(path)
    except Exception:
        tmp_path.unlink(missing_ok=True)
        raise


def revert_config(path: pathlib.Path) -> None:
    """Restore from .bak file. Raises FileNotFoundError if no backup."""
    backup = path.with_suffix(".json.bak")
    if not backup.exists():
        raise FileNotFoundError(f"backup not found: {backup}")
    shutil.copy2(backup, path)
