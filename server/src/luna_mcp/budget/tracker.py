"""In-memory budget tracker."""
from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .history import SessionHistory

PRESETS = {"warmup": 5_000, "work": 30_000, "deep_debug": 100_000}


@dataclass
class BudgetTracker:
    cap: int = 30_000
    spent: int = 0
    skipped: dict[str, int] = field(default_factory=dict)
    downgraded: dict[str, int] = field(default_factory=dict)

    def __post_init__(self):
        from .history import get_project_key
        self.session_key = get_project_key()

    def record(self, name: str, cost: int) -> None:
        self.spent += cost

    def record_skip(self, name: str) -> None:
        self.skipped[name] = self.skipped.get(name, 0) + 1

    def record_downgrade(self, src: str) -> None:
        self.downgraded[src] = self.downgraded.get(src, 0) + 1

    def remaining(self) -> int:
        return max(0, self.cap - self.spent)

    def pct(self) -> float:
        return self.spent / self.cap if self.cap > 0 else 0.0

    def status(self) -> str:
        parts = [f"spent={self.spent}/{self.cap} ({self.pct()*100:.0f}%)"]
        if self.skipped:
            parts.append("skipped=" + " ".join(f"{k}:{v}" for k, v in self.skipped.items()))
        if self.downgraded:
            parts.append("downgraded=" + " ".join(f"{k}:{v}" for k, v in self.downgraded.items()))
        return " ".join(parts)

    def reset(self) -> None:
        self.spent = 0
        self.skipped.clear()
        self.downgraded.clear()

    def on_shutdown(self, history: "SessionHistory | None") -> None:
        """Record session result to history. Call from lifespan finally."""
        if history is None:
            return
        from .history import SessionRow
        total_skip = sum(self.skipped.values())
        total_down = sum(self.downgraded.values())
        row = SessionRow(
            ts=time.time(),
            project_key=self.session_key,
            total_spent=self.spent,
            cap=self.cap,
            skipped=total_skip,
            downgraded=total_down,
            hit_cap=1 if self.spent >= self.cap else 0,
            success=1 if self.spent < self.cap * 0.95 else 0,
        )
        history.record(row)
