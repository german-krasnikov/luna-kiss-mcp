from . import maybe_expose


def register_network_tools(mcp, send_fn, bridge_getter, ensure_fn, *, exposed: set = frozenset()):
    """Register network, memory, GC tools. Returns {name: (fn, params)} for batch."""

    async def get_network_requests(count: int = 50, filter_str: str = "") -> str:
        """List recent network requests. filter_str: substring match on URL."""
        await ensure_fn()
        b = bridge_getter()
        reqs = b.get_network_requests(count, filter_str)
        if not reqs:
            return "(no requests)"
        lines = []
        for r in reqs:
            status = r.get("status", "?")
            method = r.get("method", "?")
            url = r.get("url", "?")
            lines.append(f"{status} {method} {url}")
        return "\n".join(lines)
    maybe_expose(mcp, get_network_requests, exposed)

    async def get_memory_info() -> str:
        """Heap usage + optional Luna graphics stats."""
        await ensure_fn()
        b = bridge_getter()
        result = await b.send_cdp("Runtime.getHeapUsage")
        heap = result.get("result", result)
        used = heap.get("usedSize", 0)
        total = heap.get("totalSize", 0)
        lines = [f"heap_used: {used // 1024}KB", f"heap_total: {total // 1024}KB"]
        try:
            stats = await send_fn(
                "(() => { try { var d = pc.Application.getApplication().graphicsDevice;"
                " return 'vram:' + (d._vram||0) + ' drawCalls:' + (d.drawCallsPerFrame||0); }"
                " catch(e) { return 'n/a'; } })()"
            )
            if stats and stats != "n/a":
                lines.append(f"gpu: {stats}")
        except Exception:
            pass
        return "\n".join(lines)
    maybe_expose(mcp, get_memory_info, exposed)

    async def trigger_gc() -> str:
        """Force garbage collection. Returns before/after heap sizes."""
        await ensure_fn()
        b = bridge_getter()
        before = await b.send_cdp("Runtime.getHeapUsage")
        try:
            await b.send_cdp("HeapProfiler.collectGarbage")
        except Exception:
            return "GC not available"
        after = await b.send_cdp("Runtime.getHeapUsage")
        b_used = before.get("result", before).get("usedSize", 0)
        a_used = after.get("result", after).get("usedSize", 0)
        freed = b_used - a_used
        return f"before: {b_used // 1024}KB\nafter: {a_used // 1024}KB\nfreed: {freed // 1024}KB"
    maybe_expose(mcp, trigger_gc, exposed)

    return {
        "get_network_requests": (get_network_requests, None),
        "get_memory_info": (get_memory_info, None),
        "trigger_gc": (trigger_gc, None),
    }
