try:
    from mcp.types import ToolAnnotations
    _HAS_ANNOTATIONS = True
except ImportError:
    _HAS_ANNOTATIONS = False


def maybe_expose(mcp, fn, exposed: set, *, name: str = "", read_only: bool = True):
    """Register fn as MCP tool if name (or fn.__name__) is in the exposed set."""
    if (name or fn.__name__) in exposed:
        if _HAS_ANNOTATIONS:
            annotations = ToolAnnotations(
                readOnlyHint=read_only,
                destructiveHint=not read_only,
                openWorldHint=True,
            )
            mcp.tool(annotations=annotations)(fn)
        else:
            mcp.tool()(fn)
