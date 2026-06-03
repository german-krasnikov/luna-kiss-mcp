"""F2: luna_debug native channel — enumerate and invoke pc.Debugger namespaces."""
from . import maybe_expose


def register_debug_native_tools(mcp, call_fn, *, exposed: set = frozenset()):
    async def luna_debug_discover() -> str:
        """Enumerate pc.Debugger namespaces and available methods."""
        return await call_fn("enumerateDebugger")

    async def luna_debug_invoke(type: str, name: str, params_json: str = "{}") -> str:
        """Invoke a pc.Debugger message by type/name with JSON params."""
        return await call_fn("invokeDebugger", type, name, params_json)

    maybe_expose(mcp, luna_debug_discover, exposed, read_only=True)
    maybe_expose(mcp, luna_debug_invoke, exposed, read_only=False)
    return {
        "luna_debug_discover": (luna_debug_discover, None),
        "luna_debug_invoke": (luna_debug_invoke, None),
    }
