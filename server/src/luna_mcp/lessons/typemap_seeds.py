"""Playworks-specific seed lessons keyed by class+signature."""
from .store import Lesson

PLAYWORKS_SEEDS = [
    {
        "class_name": "UnityEngine.UI.Button",
        "signature": {"methods": ["OnClick"], "fields": ["onClick", "_target", "interactable"]},
        "lesson": Lesson(
            build_hash="*", cmd="set_property", pattern_kind="playworks_button",
            situation="onClick",
            action="m_PersistentCalls invisible after transpile; access via Bridge.Reflection.getMembers on the transpiled button handler",
            token_cost=1500,
        ),
    },
    {
        "class_name": "UnityEngine.AnimatorController",
        "signature": {"methods": ["Update"], "fields": ["layers", "_runtimeAnimatorController"]},
        "lesson": Lesson(
            build_hash="*", cmd="get_component", pattern_kind="playworks_animator",
            situation="layers",
            action="Use animator._runtimeAnimatorController.layers; layer.stateMachine.states[].state.motion enumerates clips",
            token_cost=2000,
        ),
    },
    {
        "class_name": "UnityEngine.UI.Image",
        "signature": {"methods": ["SetMaterialDirty", "SetVerticesDirty"], "fields": ["fillAmount", "color", "sprite"]},
        "lesson": Lesson(
            build_hash="*", cmd="set_property", pattern_kind="playworks_image",
            situation="fillAmount",
            action="After mutating fillAmount call image.SetMaterialDirty() and image.SetVerticesDirty(); else canvas wont rebuild",
            token_cost=1000,
        ),
    },
    {
        "class_name": "UnityEngine.RectTransform",
        "signature": {"methods": ["GetWorldCorners"], "fields": ["anchoredPosition", "anchorMin", "anchorMax"]},
        "lesson": Lesson(
            build_hash="*", cmd="set_transform", pattern_kind="playworks_rect",
            situation="position",
            action="RectTransform under Canvas — use anchoredPosition (Vector2) not localPosition; localPosition silently ignored when anchorMin!=anchorMax",
            token_cost=800,
        ),
    },
    {
        "class_name": "UnityEngine.ParticleSystem",
        "signature": {"methods": ["Play", "Stop"], "fields": ["main", "emission"]},
        "lesson": Lesson(
            build_hash="*", cmd="set_property", pattern_kind="playworks_particles",
            situation="loop",
            action="Looping is in main module: ps.main.loop=true via main module struct copy + assign back; direct ps.loop has no effect",
            token_cost=600,
        ),
    },
]


def seed_typemap_lessons(store) -> int:
    """Seed Playworks-specific lessons. Idempotent via UPSERT."""
    from .keys import class_hash, sig_hash
    for entry in PLAYWORKS_SEEDS:
        ch = class_hash(entry["class_name"])
        sh = sig_hash(entry["signature"])
        store.add_typemap(entry["lesson"], ch, sh, "seed", source="seed")
    return len(PLAYWORKS_SEEDS)
