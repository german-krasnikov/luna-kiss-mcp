import logging

logger = logging.getLogger(__name__)


class Debugger:
    def __init__(self, bridge):
        self._bridge = bridge
        self._enabled = False

    async def enable(self) -> None:
        if not self._enabled:
            await self._bridge.send_cdp("Debugger.enable")
            self._enabled = True

    async def set_breakpoint(self, url_regex: str, line: int) -> str:
        await self.enable()
        result = await self._bridge.send_cdp("Debugger.setBreakpointByUrl", {
            "urlRegex": url_regex,
            "lineNumber": line - 1,
        })
        return result["result"]["breakpointId"]

    async def remove_breakpoint(self, breakpoint_id: str) -> None:
        await self._bridge.send_cdp("Debugger.removeBreakpoint", {
            "breakpointId": breakpoint_id,
        })

    async def pause(self) -> None:
        await self.enable()
        await self._bridge.send_cdp("Debugger.pause")

    async def resume(self) -> None:
        await self._bridge.send_cdp("Debugger.resume")
        self._bridge._debugger_paused = None

    def get_call_stack(self) -> str:
        state = self._bridge._debugger_paused
        if not state:
            return "(not paused)"
        frames = state.get("callFrames", [])
        lines = []
        for i, frame in enumerate(frames):
            func = frame.get("functionName") or "(anonymous)"
            loc = frame.get("location", {})
            url = frame.get("url", "")
            filename = url.rsplit("/", 1)[-1] if url else "?"
            line_num = loc.get("lineNumber", 0) + 1
            lines.append(f"#{i} {func} ({filename}:{line_num})")
        return "\n".join(lines) or "(empty stack)"

    async def get_scope_variables(self, frame_index: int = 0) -> str:
        state = self._bridge._debugger_paused
        if not state:
            return "(not paused)"
        frames = state.get("callFrames", [])
        if frame_index >= len(frames):
            return f"error: frame {frame_index} not found (stack has {len(frames)} frames)"
        frame = frames[frame_index]
        scope_chain = frame.get("scopeChain", [])
        local = next((s for s in scope_chain if s.get("type") == "local"), None)
        if not local:
            return "(no local scope)"
        object_id = local.get("object", {}).get("objectId")
        if not object_id:
            return "(no scope object)"
        result = await self._bridge.send_cdp("Runtime.getProperties", {
            "objectId": object_id,
            "ownProperties": True,
        })
        props = result.get("result", {}).get("result", [])
        lines = []
        for p in props:
            name = p.get("name", "?")
            val = p.get("value", {})
            val_type = val.get("type", "")
            if val_type in ("string", "number", "boolean"):
                lines.append(f"{name}: {val.get('value', '')}")
            elif val_type == "undefined":
                lines.append(f"{name}: undefined")
            elif val_type == "object":
                desc = val.get("description", val.get("className", "object"))
                lines.append(f"{name}: {desc}")
            else:
                lines.append(f"{name}: ({val_type})")
        return "\n".join(lines) or "(no variables)"
