"""Rules 1-10 for ToolHinter — extracted to keep hinter.py under 200 lines."""
from __future__ import annotations


def _r1_eval_spam(hist, name, kw, tag):
    if name != "eval_js":
        return None
    last3 = [c for c in hist if c.name == "eval_js"][-3:]
    if len(last3) < 3:
        return None
    prefixes = [c.key.split(":", 1)[1][:60] for c in last3]
    if len(set(prefixes)) == 1:
        return "eval_js spam — use find_objects/get_component"


def _r2_screenshot_noop(hist, name, kw, tag):
    if name != "screenshot":
        return None
    hist_list = list(hist)
    if len(hist_list) < 2:
        return None
    prev = hist_list[-2]
    if prev.name != "screenshot":
        return None
    muts = {"set_property", "set_transform", "eval_js", "simulate_click", "resume_game"}
    between = [c for c in hist_list[:-1] if c.name in muts]
    if not between:
        return "scene unchanged — try visual_diff/visual_summary instead"


def _r3_console_polling(hist, name, kw, tag):
    if name != "get_console":
        return None
    recent = [c for c in list(hist)[-4:] if c.name == "get_console"]
    if len(recent) >= 3:
        return "console polling — use watch tool with regex pattern"


def _r4_lost_context_after_find(hist, name, kw, tag):
    if name != "find_objects":
        return None
    last5 = list(hist)[-5:]
    if len(last5) < 3:
        return None
    names = [c.name for c in last5]
    if names.count("find_objects") >= 2 and "get_hierarchy" in names:
        first_idx = names.index("find_objects")
        if "get_hierarchy" in names[first_idx + 1:]:
            return "you're losing path context — cache result from find_objects"


def _r5_repeated_set_property(hist, name, kw, tag):
    if name != "set_property":
        return None
    last4 = [c for c in list(hist)[-4:] if c.name == "set_property"]
    if len(last4) >= 4:
        paths = [c.key for c in last4]
        if len(set(paths)) == 1:
            return "4× set_property on same path — use batch tool"


def _r6_detail_redundant(hist, name, kw, tag):
    if name != "get_component":
        return None
    hist_list = list(hist)
    if len(hist_list) < 2:
        return None
    prev = hist_list[-2]
    if prev.name == "get_object_detail":
        prev_path = prev.key.split(":", 1)[-1] if ":" in prev.key else prev.key
        if prev_path == kw.get("path", ""):
            return "use get_object_detail (includes components)"


def _r7_som_bypass(hist, name, kw, tag):
    if name != "eval_js":
        return None
    hist_list = list(hist)
    if len(hist_list) < 2:
        return None
    if hist_list[-2].name == "screenshot_som":
        return "use click_marker(id) instead of eval_js after screenshot_som"


def _r8_pause_leak(hist, name, kw, tag):
    hist_list = list(hist)
    pause_idxs = [i for i, c in enumerate(hist_list) if c.name == "pause_game"]
    resume_idxs = [i for i, c in enumerate(hist_list) if c.name == "resume_game"]
    if not pause_idxs:
        return None
    last_pause = pause_idxs[-1]
    last_resume = resume_idxs[-1] if resume_idxs else -1
    if last_pause > last_resume and len(hist_list) - last_pause >= 8:
        return "pause without resume — mutations may not apply"


def _r9_diag_thrash(hist, name, kw, tag):
    if name != "diagnose_object":
        return None
    hist_list = list(hist)
    recent = [c for c in hist_list[-3:] if c.name == "diagnose_object"]
    if len(recent) >= 2:
        paths = {c.key for c in recent}
        had_reflect = any(c.out_tag == "REFLECT" for c in hist_list)
        if len(paths) >= 2 and had_reflect:
            return "fix REFLECT root cause, don't scan neighbors"


def _r10_budget_deaf(hist, name, kw, tag):
    hist_list = list(hist)
    if len(hist_list) < 2:
        return None
    prev = hist_list[-2]
    if prev.name == name and prev.out_tag == "BUDGET":
        return "budget said skip — repeating same call won't help"


_RULES_BASE = [
    ("eval-spam", _r1_eval_spam),
    ("noop-screenshot", _r2_screenshot_noop),
    ("console-poll", _r3_console_polling),
    ("lost-context", _r4_lost_context_after_find),
    ("batch-mutations", _r5_repeated_set_property),
    ("detail-redundant", _r6_detail_redundant),
    ("som-bypass", _r7_som_bypass),
    ("pause-leak", _r8_pause_leak),
    ("diag-thrash", _r9_diag_thrash),
    ("budget-deaf", _r10_budget_deaf),
]
