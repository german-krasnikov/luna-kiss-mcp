"""Tests for stats_tools mcp_stats tool."""
import pytest

import luna_mcp.tools.stats_tools as stats_mod
from luna_mcp.budget.metrics import MetricsRegistry


@pytest.fixture(autouse=True)
def reset_globals():
    orig_metrics = stats_mod._metrics
    yield
    stats_mod._metrics = orig_metrics


@pytest.mark.asyncio
async def test_mcp_stats_degraded_when_no_metrics():
    stats_mod._metrics = None
    result = await stats_mod.mcp_stats()
    assert "[DEGRADED" in result


@pytest.mark.asyncio
async def test_mcp_stats_returns_report():
    m = MetricsRegistry(cap=1000)
    m.record_call("foo", 100, 50.0)
    stats_mod._metrics = m
    result = await stats_mod.mcp_stats()
    assert "100/1000" in result


@pytest.mark.asyncio
async def test_mcp_stats_token_budget():
    """Result must be ≤300 tokens (~1200 chars) for a typical run."""
    m = MetricsRegistry(cap=30_000)
    for i in range(10):
        m.record_call(f"tool_{i}", i * 100, float(i * 50))
    stats_mod._metrics = m
    result = await stats_mod.mcp_stats()
    assert len(result) < 1200
