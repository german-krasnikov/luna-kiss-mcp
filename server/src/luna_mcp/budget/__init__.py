"""Cost Budget + Adaptive Routing for Luna MCP."""
from __future__ import annotations

import os
import pathlib

from .registry import TOOL_COSTS, ToolCost, cost_of, DEFAULT  # noqa: F401
from .tracker import BudgetTracker, PRESETS
from .router import ToolRouter, Decision  # noqa: F401

__all__ = [
    "TOOL_COSTS", "ToolCost", "cost_of", "DEFAULT",
    "BudgetTracker", "PRESETS",
    "ToolRouter", "Decision",
    "init_budget",
]


def _init_budget_auto() -> tuple[BudgetTracker, ToolRouter]:
    from .history import SessionHistory, get_project_key
    from .autotune import compute_cap, estimate_p_success
    from luna_mcp.config import data_dir as _cfg_data_dir
    data_dir = _cfg_data_dir()
    db_path = data_dir / "history.db"
    history = SessionHistory(db_path)
    key = get_project_key()
    rows = history.recent(key, limit=30)
    cap = compute_cap(rows)
    p_success = estimate_p_success(rows)
    tracker = BudgetTracker(cap=cap)
    tracker._history = history
    router = ToolRouter(tracker, sigmoid_p_success=p_success)
    return tracker, router


def init_budget(mode: str | None = None) -> tuple[BudgetTracker, ToolRouter]:
    """Create tracker+router. mode: warmup|work|deep_debug|auto or reads LUNA_BUDGET_MODE."""
    resolved = mode or os.environ.get("LUNA_BUDGET_MODE", "work")
    if resolved == "auto":
        return _init_budget_auto()
    cap = PRESETS.get(resolved, PRESETS["work"])
    tracker = BudgetTracker(cap=cap)
    router = ToolRouter(tracker)
    return tracker, router
