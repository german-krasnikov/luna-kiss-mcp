"""S4.2 Emulation tools — CPU throttle + device metrics override."""
from . import maybe_expose


def register_emulation_tools(mcp, get_bridge, *, exposed: set = frozenset()):
    async def set_cpu_throttle(rate: float = 4.0) -> str:
        """Emulation.setCPUThrottlingRate — slow down JS execution. rate>=1."""
        bridge = get_bridge()
        if bridge is None:
            return "[DEGRADED] not connected"
        if rate < 1:
            return "[INVALID] rate must be >= 1 (1=no throttle, 4=4x slower)"
        try:
            await bridge.send_cdp("Emulation.setCPUThrottlingRate", {"rate": rate})
            return f"OK cpu throttle {rate}x (call clear_emulation to reset)"
        except Exception as e:
            return f"[DEGRADED] {e}"

    maybe_expose(mcp, set_cpu_throttle, exposed, read_only=False)

    async def set_device_metrics(
        width: int = 360, height: int = 640, dpr: float = 2.0, mobile: bool = True
    ) -> str:
        """Emulation.setDeviceMetricsOverride — simulate mobile screen."""
        bridge = get_bridge()
        if bridge is None:
            return "[DEGRADED] not connected"
        try:
            await bridge.send_cdp("Emulation.setDeviceMetricsOverride", {
                "width": width,
                "height": height,
                "deviceScaleFactor": dpr,
                "mobile": mobile,
            })
            return f"OK device {width}x{height} dpr={dpr} mobile={mobile} (call clear_emulation to reset)"
        except Exception as e:
            return f"[DEGRADED] {e}"

    maybe_expose(mcp, set_device_metrics, exposed, read_only=False)

    async def clear_emulation() -> str:
        """Reset CPU throttle and device metrics overrides."""
        bridge = get_bridge()
        if bridge is None:
            return "[DEGRADED] not connected"
        try:
            await bridge.send_cdp("Emulation.setCPUThrottlingRate", {"rate": 1})
            await bridge.send_cdp("Emulation.clearDeviceMetricsOverride")
            return "OK emulation cleared"
        except Exception as e:
            return f"[DEGRADED] {e}"

    maybe_expose(mcp, clear_emulation, exposed, read_only=False)

    return {
        "set_cpu_throttle": (set_cpu_throttle, None),
        "set_device_metrics": (set_device_metrics, None),
        "clear_emulation": (clear_emulation, None),
    }
