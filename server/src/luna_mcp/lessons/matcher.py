"""Semantic pattern matching for lessons."""
import re
from typing import Optional


def matches(situation_pattern: str, error_text: str) -> bool:
    """Return True if error_text matches the regex pattern (substr fallback on invalid regex)."""
    try:
        return bool(re.search(situation_pattern, error_text or ""))
    except re.error:
        return situation_pattern in (error_text or "")


def find_lesson_for_class(store, cmd: str, js_class_name: str, situation_hint: str = "") -> Optional[str]:
    """Find best typemap lesson for class + cmd. Returns 'LESSON: ...' hint or None."""
    if not js_class_name:
        return None
    from .keys import class_hash
    ch = class_hash(js_class_name)
    lessons = store.find_typemap(cmd, ch, situation_hint)
    if not lessons:
        return None
    return f"LESSON: {lessons[0].action[:120]}"
