"""TDD tests for CostCalibrator (feature #8: Budget Auto-tuning)."""
import pytest


def test_record_actual_warmup_running_mean():
    from luna_mcp.budget.calibrator import CostCalibrator
    c = CostCalibrator()
    for v in [100, 200, 300]:
        c.record_actual("ping", v)
    # n=3, running mean = 200
    assert c._ema["ping"] == pytest.approx(200.0)
    assert c._n["ping"] == 3


def test_record_actual_after_n5_uses_ema():
    from luna_mcp.budget.calibrator import CostCalibrator
    c = CostCalibrator()
    # warmup: 5 calls with value 100
    for _ in range(5):
        c.record_actual("tool", 100)
    assert c._n["tool"] == 5
    # next call with 200 → EMA: 0.7*100 + 0.3*200 = 130
    c.record_actual("tool", 200)
    assert c._ema["tool"] == pytest.approx(130.0)


def test_calibrated_cost_returns_initial_when_n_lt_5():
    from luna_mcp.budget.calibrator import CostCalibrator
    c = CostCalibrator()
    c.record_actual("tool", 50)
    assert c.calibrated_cost("tool", 100) == 100


def test_calibrated_cost_returns_initial_for_unknown_tool():
    from luna_mcp.budget.calibrator import CostCalibrator
    c = CostCalibrator()
    assert c.calibrated_cost("unknown_tool", 500) == 500


def test_calibrated_cost_blends_ema_and_initial():
    from luna_mcp.budget.calibrator import CostCalibrator
    c = CostCalibrator()
    for _ in range(5):
        c.record_actual("tool", 80)  # ema stabilises at 80
    result = c.calibrated_cost("tool", 100)
    # 0.7*80 + 0.3*100 = 86
    assert result == pytest.approx(86, abs=2)


def test_stats_returns_summary():
    from luna_mcp.budget.calibrator import CostCalibrator
    c = CostCalibrator()
    for _ in range(3):
        c.record_actual("ping", 10)
    s = c.stats()
    assert "ping" in s
    assert s["ping"]["n"] == 3
    assert "ema" in s["ping"]


def test_stats_empty():
    from luna_mcp.budget.calibrator import CostCalibrator
    c = CostCalibrator()
    assert c.stats() == {}


def test_multiple_tools_tracked_independently():
    from luna_mcp.budget.calibrator import CostCalibrator
    c = CostCalibrator()
    for _ in range(6):
        c.record_actual("ping", 10)
        c.record_actual("screenshot", 1000)
    assert c._n["ping"] == 6
    assert c._n["screenshot"] == 6
    assert c._ema["ping"] < c._ema["screenshot"]
