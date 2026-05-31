"""Thin wrapper around regression/differ.py for PNG comparison."""
from __future__ import annotations

import pathlib
from typing import Optional


async def diff_pngs(path_a: pathlib.Path, path_b: pathlib.Path) -> Optional[float]:
    """Compare two PNG/JPG files. Returns diff pct (0-100) or None on error."""
    if not path_a.exists() or not path_b.exists():
        return None
    if path_a.suffix.lower() not in (".png", ".jpg", ".webp"):
        return None
    try:
        from luna_mcp.regression.differ import diff_pct
        with open(path_b, "rb") as f:
            current_bytes = f.read()
        pct, err = diff_pct(path_a, current_bytes)
        return None if err else pct
    except Exception:
        return None
