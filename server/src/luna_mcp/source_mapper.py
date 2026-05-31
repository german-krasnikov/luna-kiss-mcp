import re

from .cdp_bridge import CDPBridge
from .debugger import Debugger

_FRAME_RE = re.compile(r'at\s+(.+?)\s+\((.+?):(\d+)(?::(\d+))?\)')


class SourceMapper:
    def __init__(self, bridge: CDPBridge, debugger: Debugger, typemap_resolver=None):
        self._bridge = bridge
        self._debugger = debugger
        self._source_cache: dict[str, str] = {}  # scriptId -> source text
        self._typemap_resolver = typemap_resolver

    async def _enable(self) -> None:
        await self._debugger.enable()

    def _find_script_id(self, filename: str) -> str | None:
        for url, sid in self._bridge._scripts.items():
            if filename in url:
                return sid
        return None

    async def _get_source(self, script_id: str) -> str:
        if script_id in self._source_cache:
            return self._source_cache[script_id]
        result = await self._bridge.send_cdp("Debugger.getScriptSource", {"scriptId": script_id})
        source = result.get("result", {}).get("scriptSource", "")
        self._source_cache[script_id] = source
        return source

    async def _search(self, script_id: str, query: str) -> list[dict]:
        result = await self._bridge.send_cdp("Debugger.searchInContent", {
            "scriptId": script_id,
            "query": query,
            "caseSensitive": True,
            "isRegex": False,
        })
        return result.get("result", {}).get("result", [])

    def _parse_frames(self, text: str) -> list[dict]:
        frames = []
        for m in _FRAME_RE.finditer(text):
            frames.append({
                "func": m.group(1),
                "file": m.group(2).rsplit("/", 1)[-1],
                "line": int(m.group(3)),
                "col": int(m.group(4)) if m.group(4) else None,
            })
        return frames

    def _classify_frame(self, func_name: str) -> str:
        if func_name.startswith("Bridge."):
            return "bridge"
        if func_name.startswith("System."):
            return "system"
        if "." in func_name:
            return "csharp"
        return "unknown"

    async def resolve_stack(self, stack_text: str) -> str:
        await self._enable()
        frames = self._parse_frames(stack_text)
        if not frames:
            return "No stack frames found"

        lines = [f"== Stack Trace ({len(frames)} frames) =="]
        for i, frame in enumerate(frames):
            kind = self._classify_frame(frame["func"])
            label = f" [{kind}]" if kind != "csharp" else ""
            lines.append(f"#{i} {frame['func']}{label}")
            lines.append(f"   JS: {frame['file']}:{frame['line']}")

            if kind == "csharp" and "UnityScriptsCompiler" in frame["file"]:
                sid = self._find_script_id("UnityScriptsCompiler")
                if sid:
                    start_m = await self._search(sid, f"/*{frame['func']} start.*/")
                    end_m = await self._search(sid, f"/*{frame['func']} end.*/")
                    if start_m and end_m:
                        sl = start_m[0]["lineNumber"] + 1
                        el = end_m[0]["lineNumber"] + 1
                        offset = frame["line"] - sl
                        lines.append(f"   method: lines {sl}-{el} ({el - sl} lines, offset {offset})")
        return "\n".join(lines)

    async def get_source_context(self, class_name: str, method_name: str = "", lines_around: int = 5) -> str:
        await self._enable()
        full_name = f"{class_name}.{method_name}" if method_name else class_name
        sid = self._find_script_id("UnityScriptsCompiler")
        if not sid:
            return "UnityScriptsCompiler.js not found in loaded scripts"

        start_m = await self._search(sid, f"/*{full_name} start.*/")
        end_m = await self._search(sid, f"/*{full_name} end.*/")
        if not start_m:
            return f"Method marker not found: {full_name}"

        start_line = start_m[0]["lineNumber"]
        end_line = end_m[0]["lineNumber"] if end_m else start_line + 50

        source = await self._get_source(sid)
        all_lines = source.split("\n")
        from_line = max(0, start_line - 1)
        to_line = min(len(all_lines), end_line + 2)

        result_lines = [f"== {full_name} (JS lines {from_line + 1}-{to_line}) =="]
        for idx in range(from_line, to_line):
            result_lines.append(f"{idx + 1}: {all_lines[idx]}")
        return "\n".join(result_lines)

    async def find_method(self, class_name: str, method_name: str = "") -> str:
        await self._enable()
        full_name = f"{class_name}.{method_name}" if method_name else class_name
        sid = self._find_script_id("UnityScriptsCompiler")
        if not sid:
            return "UnityScriptsCompiler.js not found"

        start_m = await self._search(sid, f"/*{full_name} start.*/")
        end_m = await self._search(sid, f"/*{full_name} end.*/")

        if not start_m:
            fallback = await self._search(sid, full_name)
            if fallback:
                refs = [f"  line {m['lineNumber'] + 1}: {m['lineContent'][:80]}" for m in fallback[:5]]
                return f"{full_name} (no markers, {len(fallback)} references):\n" + "\n".join(refs)
            # Try typemap fallback: resolve JS name and search for it
            if self._typemap_resolver and method_name:
                js_name = self._typemap_resolver.resolve_js_name(class_name, method_name)
                if js_name:
                    short_js = js_name.rsplit(".", 1)[-1]
                    fallback = await self._search(sid, short_js)
                    if fallback:
                        refs = [f"  line {m['lineNumber'] + 1}: {m['lineContent'][:80]}" for m in fallback[:5]]
                        return f"{full_name} (via typemap: {js_name}, {len(fallback)} refs):\n" + "\n".join(refs)
            return f"Method not found: {full_name}"

        start = start_m[0]["lineNumber"] + 1
        end = end_m[0]["lineNumber"] + 1 if end_m else "?"
        length = (end - start) if isinstance(end, int) else "?"
        return (
            f"{full_name}\n"
            f"  file: UnityScriptsCompiler.js\n"
            f"  scriptId: {sid}\n"
            f"  start: {start}\n"
            f"  end: {end}\n"
            f"  length: {length} lines"
        )
