"""Find Luna's config.json.

Priority:
  1. LUNA_PLUGIN_PATH env (may be a dir or point directly to config.json)
  2. Scan cwd upward 5 levels for config.json
"""
from __future__ import annotations

import os
import pathlib
from typing import Optional


def find_config() -> Optional[pathlib.Path]:
    env = os.environ.get("LUNA_PLUGIN_PATH")
    if env:
        p = pathlib.Path(env).expanduser().resolve()
        if p.is_file() and p.name == "config.json":
            return p
        if p.is_dir():
            candidate = p / "config.json"
            if candidate.exists():
                return candidate
        return None

    cur = pathlib.Path.cwd().resolve()
    for _ in range(5):
        candidate = cur / "config.json"
        if candidate.exists():
            return candidate
        if cur.parent == cur:
            break
        cur = cur.parent
    return None
