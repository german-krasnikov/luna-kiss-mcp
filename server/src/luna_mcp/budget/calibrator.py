"""CostCalibrator: EMA-based actual-cost tracking per tool."""
from __future__ import annotations


class CostCalibrator:
    """Track actual output tokens per tool using running mean (warmup) then EMA."""

    def __init__(self):
        self._ema: dict[str, float] = {}
        self._n: dict[str, int] = {}

    def record_actual(self, name: str, actual_out_tokens: int) -> None:
        n = self._n.get(name, 0) + 1
        prev = self._ema.get(name, float(actual_out_tokens))
        if n < 5:
            new = (prev * (n - 1) + actual_out_tokens) / n
        else:
            new = 0.7 * prev + 0.3 * actual_out_tokens
        self._ema[name] = new
        self._n[name] = n

    def calibrated_cost(self, name: str, initial_estimate: int) -> int:
        if self._n.get(name, 0) < 5:
            return initial_estimate
        ema = self._ema[name]
        return int(0.7 * ema + 0.3 * initial_estimate)

    def stats(self) -> dict:
        return {name: {"n": self._n[name], "ema": int(self._ema[name])} for name in self._n}
