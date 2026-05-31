"""MCP tools for Watchdog / Runtime Anomaly Detector (F20)."""
from __future__ import annotations

from luna_mcp.tools import maybe_expose


def register_watchdog_tools(mcp, *, get_brain_scanner, exposed=frozenset()):
    async def watchdog_report() -> str:
        """Latest anomaly detector findings."""
        scanner = get_brain_scanner()
        if not scanner or not scanner.anomalies:
            return "No anomalies detected"
        return "\n".join(scanner.anomalies)

    maybe_expose(mcp, watchdog_report, exposed, read_only=True)
    return {"watchdog_report": (watchdog_report, None)}
