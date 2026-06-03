"""S3.3 Lifecycle waiter + stream tools."""
from . import maybe_expose


def register_lifecycle_tools(mcp, call_fn, *, exposed: set = frozenset()):
    """Register lifecycle tools. Returns {name: (fn, params)} for batch."""

    async def wait_for_lifecycle(event: str, timeout_ms: int = 10000) -> str:
        """Wait for a Luna lifecycle event. Returns fired/timeout status."""
        if not event:
            return "[INVALID: event name required]"
        timeout_ms = max(1, timeout_ms)
        try:
            raw = await call_fn("waitForLunaEvent", event, timeout_ms)
        except Exception as e:
            return f"[DEGRADED:lifecycle:{e}]"
        raw = str(raw or "")
        if raw.startswith("already:"):
            t = raw.split(":", 1)[1]
            return f"fired (already, t={t}ms)"
        if raw.startswith("fired:"):
            t = raw.split(":", 1)[1]
            return f"fired (t={t}ms)"
        if raw.startswith("timeout:"):
            n = raw.split(":", 1)[1]
            return f"TIMEOUT after {n}ms waiting for {event}"
        return raw
    maybe_expose(mcp, wait_for_lifecycle, exposed, read_only=True)

    async def lifecycle_events(since_ms: int = 0) -> str:
        """Return Luna lifecycle events since since_ms. Lazily hooks lifecycle via tapLifecycle."""
        try:
            await call_fn("tapLifecycle")
            raw = await call_fn("getLifecycleEvents", since_ms)
        except Exception as e:
            return f"[DEGRADED:lifecycle:{e}]"
        raw = str(raw or "").strip()
        if not raw:
            return "[no lifecycle events]"
        return raw
    maybe_expose(mcp, lifecycle_events, exposed, read_only=True)

    return {
        "wait_for_lifecycle": (wait_for_lifecycle, None),
        "lifecycle_events": (lifecycle_events, None),
    }
