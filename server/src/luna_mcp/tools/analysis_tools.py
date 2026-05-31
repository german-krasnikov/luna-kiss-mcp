from . import maybe_expose


def register_analysis_tools(mcp, call_fn, *, exposed: set = frozenset()):
    """Register scene analysis tools. Returns {name: (fn, params)} for batch."""

    async def raycast(x: int, y: int) -> str:
        """Cast ray from screen (x,y). Returns hit object path or 'no hit'."""
        return await call_fn("raycast", x, y)
    maybe_expose(mcp, raycast, exposed)

    async def get_canvas_info(path: str) -> str:
        """Read RectTransform, Canvas, anchors, pivot, sizeDelta for UI object."""
        return await call_fn("getCanvasInfo", path)
    maybe_expose(mcp, get_canvas_info, exposed)

    async def compare_objects(path1: str, path2: str) -> str:
        """Diff two objects: transform, components, properties. Shows differences only."""
        return await call_fn("compareObjects", path1, path2)
    maybe_expose(mcp, compare_objects, exposed)

    async def get_audio_sources() -> str:
        """List all AudioSource components: name, clip, playing, volume, loop."""
        return await call_fn("getAudioSources")
    maybe_expose(mcp, get_audio_sources, exposed)

    async def get_physics_settings() -> str:
        """Read gravity, fixed timestep, layer collision matrix."""
        return await call_fn("getPhysicsSettings")
    maybe_expose(mcp, get_physics_settings, exposed)

    async def get_deep_property(path: str, component: str, field_path: str) -> str:
        """Read nested component property via __getValueAt. E.g. field_path='emission/rateOverTime'.
        Requires Luna Debugger (Object.prototype.__getValueAt)."""
        return await call_fn("getDeepProperty", path, component, field_path)
    maybe_expose(mcp, get_deep_property, exposed)

    return {
        "raycast": (raycast, None),
        "get_canvas_info": (get_canvas_info, None),
        "compare_objects": (compare_objects, None),
        "get_audio_sources": (get_audio_sources, None),
        "get_physics_settings": (get_physics_settings, None),
        "get_deep_property": (get_deep_property, None),
    }
