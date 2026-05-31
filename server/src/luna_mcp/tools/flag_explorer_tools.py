"""MCP tools for Hidden Flags Explorer (F9)."""
from __future__ import annotations

import pathlib
from typing import Optional

from luna_mcp.flag_explorer.catalog import FlagCatalog
from luna_mcp.flag_explorer.discovery import scan_jakefile_flags
from luna_mcp.flag_explorer.recommender import FlagRecommender
from luna_mcp.tools import maybe_expose

# Module-level singletons — wired in server.py lifespan
_catalog: Optional[FlagCatalog] = None
_recommender: Optional[FlagRecommender] = None


async def discover_flags(jakefile_path: str = "") -> str:
    """Scan jakefile for flag references."""
    if jakefile_path:
        p = pathlib.Path(jakefile_path).expanduser().resolve()
    else:
        from luna_mcp.build_intel.locator import find_jakefile
        p = find_jakefile()
    if p is None or not p.exists():
        return "[INVALID: Jakefile.js not found. Pass jakefile_path or set LUNA_JAKEFILE_PATH]"
    flags = scan_jakefile_flags(p)
    if not flags:
        return "no flags discovered"
    lines = [f"discovered {len(flags)} flag references:"]
    for name, locs in sorted(flags.items()):
        shown = locs[:3]
        suffix = "..." if len(locs) > 3 else ""
        lines.append(f"  {name} ({len(locs)} locations: {', '.join(shown)}{suffix})")
    return "\n".join(lines)


async def list_flag_catalog(filter_str: str = "") -> str:
    """List known flags from catalog."""
    if _catalog is None:
        return "[DEGRADED:flag_explorer:not_initialized]"
    entries = _catalog.all()
    if filter_str:
        f = filter_str.lower()
        entries = [e for e in entries if f in e.name.lower() or f in e.description.lower()]
    if not entries:
        return "no entries match"
    lines = [f"catalog: {len(entries)} entries"]
    for e in entries[:20]:
        lines.append(f"  {e.name:30} {e.risk:6} conf={e.confidence:.2f} | {e.description}")
    if len(entries) > 20:
        lines.append(f"  ... {len(entries) - 20} more (use filter_str to narrow)")
    return "\n".join(lines)


async def lookup_flag(name: str) -> str:
    """Look up a single flag by name."""
    if _catalog is None:
        return "[DEGRADED:flag_explorer:not_initialized]"
    e = _catalog.get(name)
    if e is None:
        return f"[INVALID: flag '{name}' not in catalog]"
    side = "; ".join(e.side_effects) if e.side_effects else "none"
    return (
        f"name={e.name} risk={e.risk} confidence={e.confidence:.2f}\n"
        f"description: {e.description}\n"
        f"enables: {e.enables}\n"
        f"side_effects: {side}\n"
        f"build_size_delta: {e.build_size_delta_pct:+.1f}%\n"
        f"perf_delta: {e.perf_delta}\n"
        f"source: {e.source}"
    )


async def recommend_flags(intent: str) -> str:
    """Recommend flags matching an intent description."""
    if _recommender is None:
        return "[DEGRADED:flag_explorer:not_initialized]"
    items = _recommender.recommend(intent)
    if not items:
        return f"no flags match intent '{intent[:50]}'"
    lines = [f"recommended for: '{intent[:60]}'"]
    for e in items:
        lines.append(f"  {e.name:30} {e.risk:6} | {e.description} ({e.enables[:40]})")
    return "\n".join(lines)


def register_flag_explorer_tools(mcp, *, exposed: set = frozenset()):
    maybe_expose(mcp, discover_flags, exposed, name="discover_flags")
    maybe_expose(mcp, list_flag_catalog, exposed, name="list_flag_catalog")
    maybe_expose(mcp, lookup_flag, exposed, name="lookup_flag")
    maybe_expose(mcp, recommend_flags, exposed, name="recommend_flags")

    return {
        "discover_flags":    (discover_flags,    None),
        "list_flag_catalog": (list_flag_catalog, None),
        "lookup_flag":       (lookup_flag,       None),
        "recommend_flags":   (recommend_flags,   None),
    }
