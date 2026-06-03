"""Insights tools (S2.1): pi analytics state, events, recorder install."""
from . import maybe_expose


def register_insights_tools(mcp, call_fn, *, exposed: set = frozenset()):
    """Register insights tools. insights_record_start is batch-only."""

    async def insights_state() -> str:
        """Report window.pi analytics state: event sequence numbers and totalEvents."""
        return await call_fn("piState")
    maybe_expose(mcp, insights_state, exposed)

    async def insights_events() -> str:
        """Drain the insights ring buffer: seq|t|name|opts lines (idempotent)."""
        return await call_fn("getInsightEvents")
    maybe_expose(mcp, insights_events, exposed)

    async def insights_record_start() -> str:
        """Install ring-buffer recorder on window.pi.logEvent (batch-only, idempotent)."""
        return await call_fn("installInsightsRecorder")
    # NOT exposed — batch-only

    return {
        "insights_state": (insights_state, None),
        "insights_events": (insights_events, None),
        "insights_record_start": (insights_record_start, None),
    }
