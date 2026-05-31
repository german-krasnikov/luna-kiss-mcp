"""AutoTuner: data-driven budget cap from session history."""
from __future__ import annotations

import math

from .history import SessionRow
from .tracker import PRESETS

HARD_UPPER = 200_000


def compute_cap(rows: list[SessionRow]) -> int:
    """Return auto-tuned cap. Cold start (< 5 sessions) → 'work' preset."""
    if len(rows) < 5:
        return PRESETS["work"]

    # DB returns rows ORDER BY ts DESC (newest first) — use [:N] for newest
    recent = rows[:30]
    spent = sorted(r.total_spent for r in recent)
    n = len(spent)
    p95 = spent[min(n - 1, int(n * 0.95))]
    cap = int(p95 * 1.2)

    # Failure auto-bump: >= 20% of newest 20 hit cap and didn't succeed
    last20 = rows[:20]
    failed = [r for r in last20 if r.hit_cap and not r.success]
    if last20 and len(failed) / len(last20) >= 0.2:
        cap = int(cap * 1.3)

    # High-variance: ensure cap >= max observed
    # Single outliers don't trigger this (don't move IQR/p50 ratio when rest is tight).
    p25 = spent[int(n * 0.25)]
    p75 = spent[int(n * 0.75)]
    p50 = spent[n // 2]
    iqr = p75 - p25
    if iqr / max(p50, 1) > 0.5:
        cap = max(cap, spent[-1])

    return min(cap, HARD_UPPER)


def allow_prob(pct_spent: float, p_success: float) -> float:
    """Sigmoid probability: higher p_success shifts center right (more tolerant)."""
    center = 0.4 + 0.5 * max(0.0, min(1.0, p_success))
    k = 12
    return 1.0 / (1.0 + math.exp(k * (pct_spent - center)))


def estimate_p_success(rows: list[SessionRow]) -> float:
    """Recent success rate. Empty → 0.85 (optimistic cold start)."""
    if not rows:
        return 0.85
    # DB returns rows ORDER BY ts DESC — rows[:20] = newest 20
    recent = rows[:20]
    return sum(r.success for r in recent) / len(recent)
