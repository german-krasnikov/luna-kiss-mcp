from . import maybe_expose


def register_input_tools(mcp, bridge_getter, ensure_fn, *, exposed: set = frozenset()):
    """Register input simulation tools. Returns {name: (fn, params)} for batch."""

    async def simulate_click(x: int, y: int) -> str:
        """Click at (x,y) via CDP Input.dispatchMouseEvent."""
        await ensure_fn()
        b = bridge_getter()
        await b.send_cdp("Input.dispatchMouseEvent", params={"type": "mousePressed", "x": x, "y": y, "button": "left", "clickCount": 1})
        await b.send_cdp("Input.dispatchMouseEvent", params={"type": "mouseReleased", "x": x, "y": y, "button": "left"})
        return f"clicked ({x}, {y})"
    maybe_expose(mcp, simulate_click, exposed)

    async def simulate_touch(x: int, y: int) -> str:
        """Touch at (x,y) via CDP Input.dispatchTouchEvent."""
        await ensure_fn()
        b = bridge_getter()
        await b.send_cdp("Input.dispatchTouchEvent", params={"type": "touchStart", "touchPoints": [{"x": x, "y": y}]})
        await b.send_cdp("Input.dispatchTouchEvent", params={"type": "touchEnd", "touchPoints": []})
        return f"touched ({x}, {y})"
    maybe_expose(mcp, simulate_touch, exposed)

    async def simulate_key(key: str, modifiers: int = 0) -> str:
        """Press key via CDP Input.dispatchKeyEvent. modifiers: 1=Alt 2=Ctrl 4=Meta 8=Shift."""
        await ensure_fn()
        b = bridge_getter()
        await b.send_cdp("Input.dispatchKeyEvent", params={"type": "keyDown", "key": key, "modifiers": modifiers})
        await b.send_cdp("Input.dispatchKeyEvent", params={"type": "keyUp", "key": key, "modifiers": modifiers})
        return f"key: {key}"
    maybe_expose(mcp, simulate_key, exposed)

    return {
        "simulate_click": (simulate_click, None),
        "simulate_touch": (simulate_touch, None),
        "simulate_key": (simulate_key, None),
    }
