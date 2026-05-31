"""Tool whitelist snapshot for Haiku planner prompts."""
from typing import Optional

_WHITELIST_CACHE: Optional[str] = None


def snapshot(tool_registry: dict) -> str:
    """Format tool list for inclusion in Haiku prompt.
    Returns: 'aaa | bbb | ccc' (sorted cmd names only)."""
    global _WHITELIST_CACHE
    if _WHITELIST_CACHE is not None:
        return _WHITELIST_CACHE
    names = sorted(tool_registry.keys())
    _WHITELIST_CACHE = " | ".join(names)
    return _WHITELIST_CACHE


def reset_cache() -> None:
    global _WHITELIST_CACHE
    _WHITELIST_CACHE = None


READ_ONLY_TOOLS = frozenset({
    "find_objects", "find_objects_by_component",
    "get_object_detail", "get_component", "get_components_list", "get_hierarchy",
    "get_console", "get_performance_metrics", "get_render_stats",
    "get_game_state", "get_layers", "get_materials", "get_shader_report",
    "audit_materials", "get_audio_sources", "get_deep_property",
    "diagnose_object", "diagnose_rendering", "diagnose_bottlenecks",
    "analyze_visual", "visual_summary", "get_canvas_info",
    "get_animator_state", "ping", "get_connection_info",
    "screenshot", "describe_playable",
    "raycast", "compare_objects",
})
