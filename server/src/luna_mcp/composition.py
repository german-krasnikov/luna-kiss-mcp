"""6-layer composition stack for MCP tools."""
from __future__ import annotations

import logging
import os
import time
from typing import Any

from .budget.registry import cost_of
from .server_helpers import _maybe_inject_lesson

logger = logging.getLogger(__name__)


def _guarded(name: str, fn, guard_module):
    async def wrapped(**kw):
        guard = guard_module._GUARD
        if guard is None:
            return await fn(**kw)
        if kw.pop("_no_validate", False):
            return await fn(**kw)
        block = await guard.validate(name, kw, None)
        if block:
            return block
        return await fn(**kw)
    return wrapped


def _degraded(name: str, fn, degradation_fn):
    """degradation_fn(kw) -> str|None; called at request time to allow lifespan updates."""
    async def wrapped(*args, **kw):
        if degradation_fn is not None:
            deg = degradation_fn(kw)
            if deg:
                return deg
        return await fn(*args, **kw)
    return wrapped


def _hinted(name: str, fn, get_lessons_store, hinter, lesson_inject_cmds: set):
    """get_lessons_store() -> LessonStore|None; called at request time."""
    async def wrapped(*args, **kw):
        result = await fn(*args, **kw)
        if isinstance(result, str) and result.startswith("[skipped"):
            return result
        if isinstance(result, str):
            ls = get_lessons_store() if callable(get_lessons_store) else get_lessons_store
            if ls and name in lesson_inject_cmds:
                lesson = _maybe_inject_lesson(name, kw, ls)
                if lesson:
                    result = f"{lesson}\n{result}"
            if hinter is not None and os.environ.get("LUNA_HINTER", "1") != "0":
                hint = hinter.observe(name, kw, result)
                if hint:
                    result = f"{result}\n{hint}"
        return result
    return wrapped


def _recorded(name: str, fn, recorder):
    async def wrapped(*args, **kw):
        t0 = time.perf_counter()
        result = await fn(*args, **kw)
        if recorder.active and os.environ.get("LUNA_RECORD", "0") == "1":
            ms = int((time.perf_counter() - t0) * 1000)
            try:
                recorder.log(name, kw, str(result), ms)
            except Exception:
                logger.debug("recorder.log failed for %s", name, exc_info=True)
        return result
    return wrapped


def _gated(name: str, fn, router, tracker, all_tools: dict, observe_fn):
    async def wrapped(*args, **kw):
        if os.environ.get("LUNA_BUDGET_DISABLED") == "1":
            return await observe_fn(name, fn, kw, args)
        d = router.decide(name, kw)
        if d.action == "skip":
            return f"[skipped {name}: {d.hint}]"
        if d.action == "downgrade":
            target_fn, _ = all_tools.get(d.target, (None, None))
            if target_fn:
                out = await target_fn(*args, **kw)
                return f"{out}\n[downgraded from {name}]"
            return await observe_fn(name, fn, kw, args)
        result = await observe_fn(name, fn, kw, args)
        out_est = len(str(result)) // 4
        tracker.record(name, cost_of(name, kw).est_in + out_est)
        if d.hint:
            result = f"{result}\n[budget hint: {d.hint}]"
        return result
    return wrapped


def apply_composition(
    all_tools: dict,
    *,
    budget_router,
    budget_tracker,
    get_metrics,
    get_calibrator,
    get_watchdog,
    recorder,
    get_degradation,
    get_lessons_store,
    hinter,
    guard_module,
    reflect_fn,
    lesson_inject_cmds: set,
    reflect_cmds: set,
    budget_own: set,
    mutation_cmds: set,
    recorder_skip: set,
    hinter_skip: set,
) -> dict:
    """Apply 6-layer composition to all_tools. Returns batch registry {name: (fn, params)}.

    Mutable singletons (degradation, metrics, etc.) must be passed as getter lambdas
    so closures see post-lifespan values.
    """

    def _observe_fn(name: str, fn, kw: dict, args: tuple):
        return _observe(name, fn, kw, args,
                        get_metrics(), get_calibrator(), get_watchdog())

    registry = {}
    for name, (fn, params) in all_tools.items():
        if name in mutation_cmds:
            fn = _guarded(name, fn, guard_module)
        if reflect_fn and name in reflect_cmds:
            fn = reflect_fn(name, fn)
        if name not in budget_own:
            fn = _gated(name, fn, budget_router, budget_tracker, all_tools, _observe_fn)
        if name not in hinter_skip:
            def _make_deg_fn(n):
                def deg_fn(kw):
                    deg = get_degradation()
                    if deg is not None and os.environ.get("LUNA_DEGRADATION", "1") != "0":
                        return deg.check(n, kw)
                    return None
                return deg_fn
            fn = _degraded(name, fn, _make_deg_fn(name))
            fn = _hinted(name, fn, get_lessons_store, hinter, lesson_inject_cmds)
        if name not in recorder_skip:
            fn = _recorded(name, fn, recorder)
        registry[name] = (fn, params)

    return registry


async def _observe(name: str, fn, kw: dict, args: tuple,
                   metrics, calibrator, watchdog) -> Any:
    t0 = time.perf_counter()
    err = None
    result = ""
    try:
        result = await fn(*args, **kw)
        return result
    except Exception as e:
        err = type(e).__name__
        raise
    finally:
        latency_ms = (time.perf_counter() - t0) * 1000
        if metrics is not None:
            c = cost_of(name, kw)
            metrics.record_call(name, c.est_in + (len(str(result)) // 4 if result else 0),
                                latency_ms, err)
        if calibrator is not None and err is None and result:
            calibrator.record_actual(name, len(str(result)) // 4)
        if watchdog:
            watchdog.schedule(name, kw)
