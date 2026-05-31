"""Build hash identification for lesson scoping."""
import hashlib
import os
import pathlib
from typing import Optional

_cached: Optional[str] = None


async def get_build_hash(bridge) -> str:
    global _cached
    if _cached:
        return _cached
    # Priority 1: window.__luna_build_id
    try:
        v = await bridge.eval("window.__luna_build_id || ''")
        if v:
            _cached = hashlib.sha256(str(v).encode()).hexdigest()[:12]
            return _cached
    except Exception:
        pass
    # Priority 2: typemap plugin path mtime
    plugin = os.environ.get("LUNA_PLUGIN_PATH", "")
    if plugin:
        try:
            mtime = str(pathlib.Path(plugin).stat().st_mtime)
            _cached = hashlib.sha256((plugin + mtime).encode()).hexdigest()[:12]
            return _cached
        except Exception:
            pass
    # Priority 3: script filenames hash
    try:
        srcs = await bridge.eval(
            "Array.from(document.querySelectorAll('script[src]')).map(s=>s.src.split('/').pop()).join('|')"
        )
        if srcs:
            _cached = hashlib.sha256(str(srcs).encode()).hexdigest()[:12]
            return _cached
    except Exception:
        pass
    _cached = "default"
    return _cached


def reset_cache() -> None:
    global _cached
    _cached = None
