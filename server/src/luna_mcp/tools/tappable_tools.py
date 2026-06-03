"""Tappable tools (S2.2): why_not_tappable + hit_test."""
from . import maybe_expose


def _parse_rects(text: str) -> list[dict]:
    """Parse 'path|x|y|w|h|kind' lines; skip malformed."""
    rects = []
    for line in text.splitlines():
        parts = line.split("|")
        if len(parts) != 6:
            continue
        path, x, y, w, h, kind = parts
        try:
            rects.append({"path": path, "x": float(x), "y": float(y),
                           "w": float(w), "h": float(h), "kind": kind})
        except ValueError:
            continue
    return rects


def register_tappable_tools(mcp, call_fn, *, exposed: set = frozenset()):
    """Register tappable tools."""

    async def why_not_tappable(path: str) -> str:
        """Explain why a UI element is not tappable: interactable, CanvasGroup, raycastTarget."""
        return await call_fn("whyNotTappable", path)
    maybe_expose(mcp, why_not_tappable, exposed)

    async def hit_test(x: float, y: float) -> str:
        """Find interactive elements at screen coordinates (x, y). Returns deepest-first matches.
        Area tie-break is a heuristic (smaller area = more specific); collectInteractiveRects carries no z-order."""
        rects_text = await call_fn("collectInteractiveRects", 40)
        rects = _parse_rects(rects_text)
        hits = [r for r in rects if r["x"] <= x < r["x"] + r["w"]
                                  and r["y"] <= y < r["y"] + r["h"]]
        if not hits:
            return f"no interactable at ({x},{y})"
        # Sort deepest path first; on equal depth, smaller area first (more specific)
        hits.sort(key=lambda r: (r["path"].count("/"), -(r["w"] * r["h"])), reverse=True)
        return "\n".join(f"{r['path']}|{r['kind']}" for r in hits)
    maybe_expose(mcp, hit_test, exposed)

    return {
        "why_not_tappable": (why_not_tappable, None),
        "hit_test": (hit_test, None),
    }
