"""Tests for F3 cdp_perf_metrics tool."""
import pytest


class FakeMCP:
    def tool(self, **kw):
        def dec(fn): return fn
        return dec


# --- basic registration ---

def test_perf_tools_returns_1_entry():
    from luna_mcp.tools.perf_tools import register_perf_tools
    tools = register_perf_tools(FakeMCP(), lambda: None, exposed=set())
    assert len(tools) == 1
    assert "cdp_perf_metrics" in tools


# --- CDP call order ---

@pytest.mark.asyncio
async def test_enable_called_before_getmetrics():
    from luna_mcp.tools.perf_tools import register_perf_tools
    calls = []

    async def fake_send_cdp(method, params=None, **kw):
        calls.append(method)
        if method == "Performance.getMetrics":
            return {"result": {"metrics": [{"name": "JSHeapUsedSize", "value": 1234567}]}}
        return {}

    class FakeBridge:
        send_cdp = staticmethod(fake_send_cdp)

    tools = register_perf_tools(FakeMCP(), lambda: FakeBridge(), exposed=set())
    fn, _ = tools["cdp_perf_metrics"]
    await fn()
    assert calls[:2] == ["Performance.enable", "Performance.getMetrics"]


# --- formats selected vitals ---

@pytest.mark.asyncio
async def test_formats_selected_vitals():
    from luna_mcp.tools.perf_tools import register_perf_tools

    METRICS = [
        {"name": "JSHeapUsedSize", "value": 5000000},
        {"name": "ScriptDuration", "value": 0.042},
        {"name": "V8CompileTime", "value": 99},  # noise — should be excluded
        {"name": "Nodes", "value": 512},
    ]

    async def fake_send_cdp(method, params=None, **kw):
        if method == "Performance.getMetrics":
            return {"result": {"metrics": METRICS}}
        return {}

    class FakeBridge:
        send_cdp = staticmethod(fake_send_cdp)

    tools = register_perf_tools(FakeMCP(), lambda: FakeBridge(), exposed=set())
    fn, _ = tools["cdp_perf_metrics"]
    result = await fn()
    assert "JSHeapUsedSize=" in result
    assert "ScriptDuration=" in result
    assert "Nodes=" in result
    assert "V8CompileTime" not in result


# --- empty metrics ---

@pytest.mark.asyncio
async def test_handles_empty_metrics():
    from luna_mcp.tools.perf_tools import register_perf_tools

    async def fake_send_cdp(method, params=None, **kw):
        if method == "Performance.getMetrics":
            return {"result": {"metrics": []}}
        return {}

    class FakeBridge:
        send_cdp = staticmethod(fake_send_cdp)

    tools = register_perf_tools(FakeMCP(), lambda: FakeBridge(), exposed=set())
    fn, _ = tools["cdp_perf_metrics"]
    result = await fn()
    assert result == "(no metrics)"


# --- degraded when bridge is None ---

@pytest.mark.asyncio
async def test_perf_degraded_no_bridge():
    from luna_mcp.tools.perf_tools import register_perf_tools

    tools = register_perf_tools(FakeMCP(), lambda: None, exposed=set())
    fn, _ = tools["cdp_perf_metrics"]
    result = await fn()
    assert "[DEGRADED]" in result
