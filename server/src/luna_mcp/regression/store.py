"""Baseline I/O: save/load/list/invalidate PNG baselines + metadata."""
import asyncio
import fcntl
import hashlib
import json
import os
import pathlib
import time
import uuid
from typing import Optional

from luna_mcp.config import data_dir as _data_dir

_DATA_DIR = _data_dir()
_BASELINES_ROOT = _DATA_DIR / "baselines"

_lock = asyncio.Lock()


class BaselineStore:
    def __init__(self, root: pathlib.Path = _BASELINES_ROOT):
        self.root = root

    def _build_dir(self, build_hash: str) -> pathlib.Path:
        d = self.root / build_hash
        d.mkdir(parents=True, exist_ok=True)
        return d

    async def save(self, build_hash: str, name: str, png_bytes: bytes,
                   mask_zones: str = "", semantic_hint: str = "",
                   pixel_threshold: float = 1.0, text_signature: str = "") -> pathlib.Path:
        async with _lock:
            d = self._build_dir(build_hash)
            tmp_path = str(d / f".{uuid.uuid4().hex}.png.tmp")
            pathlib.Path(tmp_path).write_bytes(png_bytes)
            target = str(d / f"{name}.png")
            os.replace(tmp_path, target)
            meta = {
                "mask_zones": mask_zones,
                "semantic_hint": semantic_hint,
                "pixel_threshold": pixel_threshold,
                "text_signature": text_signature,
                "created_at": time.time(),
            }
            meta_path = d / f"{name}.json"
            with open(meta_path, "w") as f:
                fcntl.flock(f.fileno(), fcntl.LOCK_EX)
                try:
                    json.dump(meta, f)
                finally:
                    fcntl.flock(f.fileno(), fcntl.LOCK_UN)
            return pathlib.Path(target)

    def load(self, build_hash: str, name: str) -> Optional[tuple]:
        d = self.root / build_hash
        png = d / f"{name}.png"
        meta_path = d / f"{name}.json"
        if not png.exists() or not meta_path.exists():
            return None
        return png, json.loads(meta_path.read_text())

    def list(self, build_hash: str) -> list:
        d = self.root / build_hash
        if not d.exists():
            return []
        return sorted(p.stem for p in d.glob("*.png"))

    def invalidate(self, build_hash: str, name: str = "") -> int:
        d = self.root / build_hash
        if not d.exists():
            return 0
        if name:
            count = 0
            for p in (d / f"{name}.png", d / f"{name}.json"):
                if p.exists():
                    p.unlink()
                    count += 1
            return count
        count = sum(1 for _ in d.glob("*"))
        for p in list(d.glob("*")):
            p.unlink()
        d.rmdir()
        return count


async def get_build_hash(bridge) -> str:
    """Try iframe __luna_build_id, fallback to script src hashes."""
    try:
        v = await bridge.eval("window.__luna_build_id || ''")
        if v:
            return hashlib.sha1(str(v).encode()).hexdigest()[:16]
    except Exception:
        pass
    try:
        srcs = await bridge.eval(
            "Array.from(document.querySelectorAll('script[src]'))"
            ".map(s=>s.src.split('/').pop()).join('|')"
        )
        if srcs:
            return hashlib.sha1(str(srcs).encode()).hexdigest()[:16]
    except Exception:
        pass
    return "default"
