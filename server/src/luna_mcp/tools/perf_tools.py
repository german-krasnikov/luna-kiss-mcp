"""F3: CDP Performance.getMetrics tool."""
from . import maybe_expose

_VITALS = {
    "JSHeapUsedSize", "Nodes", "LayoutCount", "RecalcStyleCount",
    "LayoutDuration", "RecalcStyleDuration", "ScriptDuration", "TaskDuration",
    "JSEventListeners", "Documents",
}


def register_perf_tools(mcp, get_bridge, *, exposed: set = frozenset()):
    async def cdp_perf_metrics() -> str:
        """CDP Performance.getMetrics — curated vitals: heap, nodes, durations."""
        bridge = get_bridge()
        if bridge is None:
            return "[DEGRADED] bridge not connected"
        try:
            await bridge.send_cdp("Performance.enable")
            result = await bridge.send_cdp("Performance.getMetrics")
        except Exception as e:
            return f"[DEGRADED] {e}"
        metrics = result.get("result", {}).get("metrics", [])
        lines = [f"{m['name']}={m['value']}" for m in metrics if m["name"] in _VITALS]
        return "\n".join(lines) if lines else "(no metrics)"

    maybe_expose(mcp, cdp_perf_metrics, exposed, read_only=True)
    return {"cdp_perf_metrics": (cdp_perf_metrics, None)}
