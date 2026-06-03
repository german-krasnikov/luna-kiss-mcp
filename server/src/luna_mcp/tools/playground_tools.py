"""Playground field tools — session-only field edits via setField."""
from . import maybe_expose
from .modify_tools import _parse_value


def _infer_field_type(v) -> str:
    """Map Python type to Unity field type string."""
    if isinstance(v, bool):   return "boolean"
    if isinstance(v, (int, float)): return "number"
    return "string"


def register_playground_tools(mcp, call_fn, *, exposed: set = frozenset()):
    """Register playground field tools. Returns {name: (fn, params)} for batch."""

    async def set_playground_field(path: str, field: str, value: str) -> str:
        """Set a playground field value on a component at path via the debugger inspector.
        SESSION-ONLY — not persisted. Resets on reload. Use get_playground_fields to
        discover available fields from the build file."""
        coerced = _parse_value(value)
        field_type = _infer_field_type(coerced)
        result = await call_fn("setField", path, "PlaygroundFields", field, coerced, field_type)
        return f"{result}\n[session-only: not persisted, resets on reload]"
    maybe_expose(mcp, set_playground_field, exposed, read_only=False)

    return {
        "set_playground_field": (set_playground_field, None),
    }
