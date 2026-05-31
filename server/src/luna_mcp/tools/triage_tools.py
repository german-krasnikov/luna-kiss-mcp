"""F11 Smart Error Triage MCP tool."""
from luna_mcp.error_triage.triage import triage_with_llm
from luna_mcp.tools import maybe_expose


def register_triage_tools(mcp, *, get_console_fn, get_sampling, exposed: set = frozenset()):
    async def triage_console(count: int = 100) -> str:
        """Classify + dedup console errors. Returns prioritized summary."""
        raw = await get_console_fn(count=count)
        return await triage_with_llm(raw, get_sampling())

    maybe_expose(mcp, triage_console, exposed)
    return {"triage_console": (triage_console, None)}
