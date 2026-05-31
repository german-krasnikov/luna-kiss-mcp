"""Read and parse config.json."""
from __future__ import annotations

import json
import pathlib


def read_config(path: pathlib.Path) -> dict:
    """Parse config.json; raises ValueError on invalid JSON."""
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        raise ValueError(f"invalid JSON in {path}: {e}") from e
