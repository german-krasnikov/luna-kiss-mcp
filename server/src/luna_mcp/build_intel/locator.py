"""Find Jakefile.js. Priority: LUNA_JAKEFILE_PATH env → scan cwd up 5 levels."""
import os
import pathlib
from typing import Optional


def find_jakefile() -> Optional[pathlib.Path]:
    env_path = os.environ.get("LUNA_JAKEFILE_PATH")
    if env_path:
        p = pathlib.Path(env_path).expanduser().resolve()
        if p.exists() and p.is_file():
            return p
        return None
    cur = pathlib.Path.cwd().resolve()
    for _ in range(5):
        candidate = cur / "Jakefile.js"
        if candidate.exists():
            return candidate
        if cur.parent == cur:
            break
        cur = cur.parent
    return None
