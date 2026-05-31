import json
from pathlib import Path

from .cdp_bridge import CDPBridge

_JS_PATH = Path(__file__).parent.parent.parent.parent / "js" / "luna_helpers.js"


def _read_js() -> str:
    return _JS_PATH.read_text(encoding="utf-8")


_INJECT_CHECK = """
(() => {
    const iframe = document.querySelector('iframe');
    if (!iframe || !iframe.contentWindow) return 'no iframe';
    const w = iframe.contentWindow;
    if (w.__luna_mcp) return 'already injected';
    return 'need inject';
})()
"""

_INJECT_BLOB = """
(() => {{
    const iframe = document.querySelector('iframe');
    if (!iframe || !iframe.contentWindow) return 'no iframe';
    const w = iframe.contentWindow;
    const code = {code_json};
    const blob = new Blob([code], {{type: 'application/javascript'}});
    const url = URL.createObjectURL(blob);
    return new Promise((resolve) => {{
        const script = w.document.createElement('script');
        script.onload = () => {{ URL.revokeObjectURL(url); resolve(typeof w.__luna_mcp !== 'undefined' ? 'injected' : 'failed'); }};
        script.onerror = () => {{ URL.revokeObjectURL(url); resolve('inject error'); }};
        script.src = url;
        w.document.head.appendChild(script);
    }});
}})()
"""

_CHECK_EXPR = (
    "typeof document.querySelector('iframe')"
    "?.contentWindow?.__luna_mcp !== 'undefined' ? 'ok' : 'missing'"
)

_NEEDS_INJECT = "__LUNA_NEEDS_INJECT__"

_CALL_TMPL = """
(() => {{
    const iframe = document.querySelector('iframe');
    const w = iframe && iframe.contentWindow;
    if (!w || !w.__luna_mcp) return '{sentinel}';
    return w.__luna_mcp.{method}({args});
}})()
""".strip()


class LunaRuntime:
    def __init__(self, bridge: CDPBridge):
        self._bridge = bridge
        self._injected = False

    async def inject_helpers(self) -> None:
        check = await self._bridge.eval(_INJECT_CHECK)
        if check == "already injected":
            self._injected = True
            return
        if check != "need inject":
            self._last_inject_result = check
            return
        code_json = json.dumps(_read_js())
        result = await self._bridge.eval(_INJECT_BLOB.format(code_json=code_json))
        self._last_inject_result = result
        self._injected = result in ("injected", "already injected")

    async def ensure_helpers(self) -> None:
        if not self._injected:
            await self.inject_helpers()
            return
        result = await self._bridge.eval(_CHECK_EXPR)
        if result != "ok":
            self._injected = False
            await self.inject_helpers()

    async def call(self, method: str, *args, timeout: float = 30.0) -> str:
        args_str = ", ".join(json.dumps(a) for a in args)
        expr = _CALL_TMPL.format(sentinel=_NEEDS_INJECT, method=method, args=args_str)
        result = await self._bridge.eval(expr, timeout=timeout)
        if result == _NEEDS_INJECT:
            await self.inject_helpers()
            result = await self._bridge.eval(expr, timeout=timeout)
            if result == _NEEDS_INJECT:
                raise RuntimeError("luna helpers unavailable after inject attempt")
        return result
