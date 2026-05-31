"""Stats tool: MetricsRegistry summary exposed as MCP tool."""
from typing import Optional

from ..budget.metrics import MetricsRegistry

# Module-level singletons — set by server.py at startup
_metrics: Optional[MetricsRegistry] = None


async def mcp_stats() -> str:
    """Return MetricsRegistry summary. ≤300 tokens."""
    if _metrics is None:
        return "[DEGRADED:metrics:not_initialized]"
    return _metrics.format_report()


def register_stats_tools(mcp, exposed: set):
    from . import maybe_expose

    fn = mcp_stats
    maybe_expose(mcp, fn, exposed, name="mcp_stats")
    return {"mcp_stats": (fn, None)}
