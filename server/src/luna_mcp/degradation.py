"""GracefulDegradation — 3-level escalating degradation middleware."""
from typing import Callable, Optional


class GracefulDegradation:
    """3-level escalating degradation based on bridge state and metrics counters."""

    def __init__(self, bridge_getter: Callable, metrics, typemap_resolver_getter: Callable):
        self._bridge = bridge_getter
        self._metrics = metrics
        self._typemap = typemap_resolver_getter

    def check(self, name: str, kw: dict) -> Optional[str]:
        """Return [DEGRADED:level:reason] string or None."""
        # L1: Chrome down
        bridge = self._bridge()
        if bridge is None or not getattr(bridge, "connected", False):
            if name not in self._offline_safe():
                return "[DEGRADED:chrome:offline → run Chrome with --remote-debugging-port=9222]"
        # L2: typemap missing for schema-sensitive tools
        skipped = 0
        if self._metrics is not None:
            skipped = getattr(self._metrics, "skipped", {}).get("get_type_info", 0)
        if skipped >= 2:
            typemap = self._typemap()
            loaded = typemap is not None and getattr(typemap, "is_loaded", lambda: False)()
            if not loaded and name in {"set_property", "get_class_api"}:
                return "[DEGRADED:typemap:missing → fuzzy-match mode, set LUNA_PLUGIN_PATH]"
        return None

    def _offline_safe(self) -> set:
        return {
            "analyze_build", "get_build_assets", "get_build_recommendations",
            "audit_build_size", "ping", "get_connection_info",
            "template_list", "template_save",
        }
