"""Luna build/runtime issue seeds for LessonStore."""
from .store import Lesson

LUNA_ISSUE_SEEDS = [
    Lesson(
        build_hash="*", cmd="*", pattern_kind="luna_build_issue",
        situation="TypeLoadException: Could not load type",
        action="Assembly mismatch between Luna plugin and Unity version. "
               "Clean build + match Playworks plugin to Unity runtime version.",
        token_cost=2000,
    ),
    Lesson(
        build_hash="*", cmd="*", pattern_kind="luna_build_issue",
        situation="Missing shader variant|SVC_Luna shader",
        action="Luna SVC_Luna shader variant strip. Add 'SVC_Luna' to Always Included Shaders "
               "in ProjectSettings/Graphics or disable shader stripping in luna.json.",
        token_cost=1800,
    ),
    Lesson(
        build_hash="*", cmd="*", pattern_kind="luna_build_issue",
        situation="MSBuild failure|Build FAILED|error MSB",
        action="MSBuild failed during Luna transpile. Check csproj references, "
               "verify .NET SDK version matches luna.json dotnet_version, run jake build --verbose.",
        token_cost=2500,
    ),
    Lesson(
        build_hash="*", cmd="*", pattern_kind="luna_build_issue",
        situation="zero vertex colors|missing vertex colors|VertexColor undefined",
        action="Mesh vertex colors stripped at export. Enable 'Keep Vertex Colors' "
               "in MeshRenderer import settings, or set meshOptimizer.keepVertexColors=true.",
        token_cost=1200,
    ),
    Lesson(
        build_hash="*", cmd="*", pattern_kind="luna_build_issue",
        situation="OnMouseDown|OnMouseUp|OnMouseOver not firing",
        action="OnMouseDown requires Physics.Raycast infrastructure. "
               "In Luna/WebGL builds use OnPointerClick (IPointerClickHandler) via EventSystem instead.",
        token_cost=1500,
    ),
    Lesson(
        build_hash="*", cmd="*", pattern_kind="luna_build_issue",
        situation="AABB culling|object disappears|frustum culled incorrectly",
        action="Luna AABB bounds may be stale after animation. "
               "Call renderer.ResetBounds() or disable culling with mesh.bounds = new Bounds(...).",
        token_cost=1000,
    ),
]


def seed_luna_issues(store) -> int:
    """Seed Luna build/runtime issue lessons. Idempotent via UPSERT."""
    for lesson in LUNA_ISSUE_SEEDS:
        store.add(lesson, update_action=True)
    return len(LUNA_ISSUE_SEEDS)
