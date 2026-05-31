"""Luna-specific seed lessons for LessonStore."""
from .store import Lesson

LUNA_SEEDS = [
    Lesson(
        build_hash="*", cmd="set_property", pattern_kind="playworks_type",
        situation="Cannot read properties of undefined.*castToUnityType",
        action="Use TypemapResolver.get_js_class_name() before set_property; "
               "Playworks types live under window.bridge.* not global",
        token_cost=1500,
    ),
    Lesson(
        build_hash="*", cmd="*", pattern_kind="missing_helper",
        situation="__luna_mcp is undefined",
        action="Iframe re-navigated; call ping first to trigger re-injection of luna_helpers.js",
        token_cost=400,
    ),
    Lesson(
        build_hash="*", cmd="eval_js", pattern_kind="iframe_lost",
        situation="Cannot read properties of null.*contentWindow",
        action="document.querySelector('iframe') returned null — Luna build still loading; "
               "wait 500ms and retry, do NOT screenshot yet",
        token_cost=12000,
    ),
    Lesson(
        build_hash="*", cmd="*", pattern_kind="cdp_disconnect",
        situation="WebSocket is not open",
        action="CDPBridge auto-reconnect handles this; if persists, Chrome was closed — "
               "re-launch with --remote-debugging-port=9222",
        token_cost=200,
    ),
    Lesson(
        build_hash="*", cmd="set_animator_param", pattern_kind="playworks_animator",
        situation="AnimatorController state hash mismatch",
        action="Luna transpiles state names to FNV1a hashes; use edit_animator_state "
               "with state_hash from get_animator_state, NOT the C# string name",
        token_cost=2000,
    ),
]


def seed_default(store) -> int:
    """Seed Luna-specific lessons. Idempotent via UPSERT; updates action on re-seed."""
    for L in LUNA_SEEDS:
        store.add(L, update_action=True)
    return len(LUNA_SEEDS)
