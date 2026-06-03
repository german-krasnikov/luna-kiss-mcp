"""F6: diagnose_text tool — TMP diagnostics via diagnoseText JS helper."""
from . import maybe_expose


def register_text_tools(mcp, call_fn, *, exposed: set = frozenset()):
    async def diagnose_text(path: str) -> str:
        """Diagnose TextMeshPro component: overflow, missing glyphs, preferred size. read_only=False: calls ForceMeshUpdate."""
        return await call_fn("diagnoseText", path)

    maybe_expose(mcp, diagnose_text, exposed, read_only=False)
    return {"diagnose_text": (diagnose_text, None)}
