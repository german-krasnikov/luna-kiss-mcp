from . import maybe_expose


def register_reflection_tools(mcp, call_fn, *, exposed: set = frozenset()):
    """Register Bridge.Reflection + selection tools. Returns {name: (fn, params)} for batch."""

    async def get_enums(filter: str = "") -> str:
        """List Unity enums with values. Optional name filter. Requires pc.Debugger."""
        return await call_fn("getEnums", filter)
    maybe_expose(mcp, get_enums, exposed)

    async def get_type_info(type_name: str) -> str:
        """Introspect a Bridge.NET type: fields, properties, methods."""
        return await call_fn("getTypeInfo", type_name)
    maybe_expose(mcp, get_type_info, exposed)

    async def get_assemblies() -> str:
        """List available Bridge.NET assemblies."""
        return await call_fn("getAssemblies")
    maybe_expose(mcp, get_assemblies, exposed)

    async def select_object(path: str) -> str:
        """Select object in Luna Debugger Inspector."""
        return await call_fn("selectObject", path)
    maybe_expose(mcp, select_object, exposed)

    async def get_selection() -> str:
        """Get currently selected object in Luna Debugger."""
        return await call_fn("getSelection")
    maybe_expose(mcp, get_selection, exposed)

    async def get_component_fields(component_type: str) -> str:
        """Return field map definition from pc.Debugger.Components[type]. Requires Luna Debugger."""
        return await call_fn("getComponentFields", component_type)
    maybe_expose(mcp, get_component_fields, exposed)

    async def log_object(path: str) -> str:
        """Log a GameObject to browser console via pc.Debugger.Log.create. Requires Luna Debugger."""
        return await call_fn("logObject", path)
    maybe_expose(mcp, log_object, exposed)

    async def log_component(path: str, component: str) -> str:
        """Log a specific component to browser console via pc.Debugger.Log.create. Requires Luna Debugger."""
        return await call_fn("logComponent", path, component)
    maybe_expose(mcp, log_component, exposed)

    async def debugger_message(type: str, name: str, params_json: str = "{}") -> str:
        """Low-level access to any Luna Debugger endpoint via postMessage protocol.
        type: GET/POST/PATCH, name: Hierarchy/Inspector/Console/etc."""
        return await call_fn("sendDebuggerMessage", type, name, params_json)
    maybe_expose(mcp, debugger_message, exposed)

    return {
        "get_enums": (get_enums, None),
        "get_type_info": (get_type_info, None),
        "get_assemblies": (get_assemblies, None),
        "select_object": (select_object, None),
        "get_selection": (get_selection, None),
        "get_component_fields": (get_component_fields, None),
        "log_object": (log_object, None),
        "log_component": (log_component, None),
        "debugger_message": (debugger_message, None),
    }
