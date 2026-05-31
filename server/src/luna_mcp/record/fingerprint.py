"""Scene fingerprint helpers."""
import hashlib
from typing import Awaitable, Callable


async def scene_fp(call_fn: Callable[..., Awaitable[str]]) -> str:
    """Cheap scene fingerprint via snapshot_state."""
    try:
        result = await call_fn("snapshotState", "__fp__", "/")
        return hashlib.sha256(str(result).encode()).hexdigest()[:16]
    except Exception:
        return "unavailable"


def hash_result(text) -> str:
    return hashlib.sha256((text or "").encode()).hexdigest()[:16]
