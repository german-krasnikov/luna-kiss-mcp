"""Single source of truth for Haiku output normalization.

Pure functions, no state, no I/O, no async.
"""
from __future__ import annotations

import re
from typing import Literal, Optional, Tuple

OutputKind = Literal["sentinel", "description", "dsl", "verdict"]

REFUSAL_PATTERNS = (
    "i cannot ", "i can't ", "i'm unable", "i won't ",
    "i am unable", "sorry, i",
)
HEDGE_CONJUNCTIONS = (" but i ", " but the ", " however")

_FENCE_RE = re.compile(r"^\s*```(?:\w+)?\s*\n?(.*?)\n?```\s*$", re.DOTALL)
_CONV_PREFIXES = (
    "sure!", "sure,", "of course!", "of course,",
    "looking at this image,", "looking at these images,",
    "based on the image,", "based on the images,",
    "here's", "here is", "i see",
)


def is_refusal(text: str) -> bool:
    if not text:
        return False
    head = text.strip().lower()[:80]
    if any(c in head for c in HEDGE_CONJUNCTIONS):
        return False
    return any(head.startswith(p) for p in REFUSAL_PATTERNS)


def strip_fences(text: str) -> str:
    if not text:
        return text
    stripped = text.strip()
    m = _FENCE_RE.match(stripped)
    if m:
        return m.group(1).strip()
    return stripped


def strip_conversational(text: str) -> str:
    if not text:
        return text
    stripped = text.strip()
    lower = stripped.lower()
    for prefix in _CONV_PREFIXES:
        if lower.startswith(prefix):
            stripped = stripped[len(prefix):].lstrip(" ,.:")
            break
    return stripped


def normalize(text: Optional[str], kind: OutputKind = "description") -> Tuple[Optional[str], bool]:
    """Returns (normalized_text, is_refusal)."""
    if text is None:
        return None, False
    if is_refusal(text):
        return None, True

    cleaned = strip_fences(text.strip())
    cleaned = strip_conversational(cleaned)
    cleaned = strip_fences(cleaned.strip())
    cleaned = cleaned.strip()

    if not cleaned:
        return None, False

    if kind == "verdict":
        first_line = next((ln.strip() for ln in cleaned.splitlines() if ln.strip()), "")
        return first_line or None, False
    if kind == "sentinel":
        first_token = cleaned.split()[0] if cleaned.split() else ""
        return first_token or None, False
    return cleaned, False
