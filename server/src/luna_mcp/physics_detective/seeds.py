"""9 initial Luna physics lessons covering goblin/verlet/baked/unified backends."""
from luna_mcp.lessons.store import Lesson

PHYSICS_SEEDS = [
    Lesson(build_hash="*", cmd="diagnose_physics", pattern_kind="physics_goblin",
           situation="velocity reset|velocity zeros each frame",
           action="Goblin custom solver caps velocity 8m/s. Check P3 cap patch in goblin-patches.js or use Rigidbody.WakeUp()",
           token_cost=1500),
    Lesson(build_hash="*", cmd="diagnose_physics", pattern_kind="physics_goblin",
           situation="compound|child colliders ignored",
           action="Goblin compound colliders unsupported. Flatten to single OBB or separate body per child collider",
           token_cost=1200),
    Lesson(build_hash="*", cmd="diagnose_physics", pattern_kind="physics_goblin",
           situation="static kinematic|fall through moving platforms|jiggle|jiggling|shake|shaking",
           action="Use Rigidbody{isKinematic=true, ContinuousDynamic} for moving platforms",
           token_cost=1000),
    Lesson(build_hash="*", cmd="diagnose_physics", pattern_kind="physics_verlet",
           situation="rope explode|cloth explode|stiffness explode",
           action="Verlet PBD: stiffness > 0.95 unstable. Set ≤ 0.92 + iterations ≥ 8",
           token_cost=800),
    Lesson(build_hash="*", cmd="diagnose_physics", pattern_kind="physics_verlet",
           situation="anchored particles drift",
           action="Verlet: anchored particles need iterations ≥ 8 (default 4). Check solver step iterations parameter",
           token_cost=600),
    Lesson(build_hash="*", cmd="diagnose_physics", pattern_kind="physics_verlet",
           situation="jiggle|jiggles after stop|cloth jiggle",
           action="Verlet pow-based friction default 0.05 too low. Increase to 0.08 + check auto-sleep speed threshold",
           token_cost=500),
    Lesson(build_hash="*", cmd="diagnose_physics", pattern_kind="physics_baked",
           situation="playback speed|animation desync",
           action="Baked adapter: Time.timeScale mutation breaks frame interpolation. Verify bakedAdapter._timestep not corrupted",
           token_cost=900),
    Lesson(build_hash="*", cmd="diagnose_physics", pattern_kind="physics_baked",
           situation="dynamic after bake|spawned object missed",
           action="Baked dynamicList built once at Awake. Runtime spawned objects invisible to raycast. Call runtime collider rebake method",
           token_cost=1200),
    Lesson(build_hash="*", cmd="diagnose_physics", pattern_kind="physics_unified",
           situation="cross solver|hero not pushing|push radius",
           action="Unified solver: check push radius/force config values",
           token_cost=1500),
]


def seed_physics_lessons(store) -> int:
    """Idempotent seed. Returns count added/updated."""
    for lesson in PHYSICS_SEEDS:
        store.add(lesson, update_action=True)
    return len(PHYSICS_SEEDS)
