from . import maybe_expose


def register_playworks_tools(mcp, call_fn, *, exposed: set = frozenset()):
    """Register Playworks performance/diagnostics tools. Returns {name: (fn, params)} for batch."""

    async def get_performance_metrics() -> str:
        """Snapshot of runtime performance: FPS, frame time breakdown, RAM, draw calls, and load time. Targets: FPS > 30, RAM < 256 MB. Use as first step when investigating performance issues; follow up with diagnose_rendering or get_render_stats for GPU details."""
        return await call_fn("getPerformanceMetrics")
    maybe_expose(mcp, get_performance_metrics, exposed)

    async def diagnose_rendering() -> str:
        """One-shot rendering health check: WebGL version, active shaders, draw calls, cameras, and canvas resolution. Use to identify rendering setup issues. For raw frame counters only, use get_render_stats; for GPU caps, use get_gpu_info."""
        return await call_fn("diagnoseRendering")
    maybe_expose(mcp, diagnose_rendering, exposed)

    async def audit_textures() -> str:
        """Audit loaded textures: size, format, memory est. Flags >1024x1024. Sorted biggest first."""
        return await call_fn("auditTextures")
    maybe_expose(mcp, audit_textures, exposed)

    async def get_render_stats() -> str:
        """PlayCanvas frame stats: FPS, triangles, draw calls, shaders, cameras, shadow updates, timings."""
        return await call_fn("getRenderStats")
    maybe_expose(mcp, get_render_stats, exposed)

    async def get_vram_usage() -> str:
        """VRAM breakdown: textures, vertex/index/uniform buffers, GPU caps (WebGL version, max texture)."""
        return await call_fn("getVramUsage")
    maybe_expose(mcp, get_vram_usage, exposed)

    async def get_gpu_info() -> str:
        """GPU capabilities: WebGL version, vendor, renderer, texture limits, float textures, canvas size."""
        return await call_fn("getGpuInfo")
    maybe_expose(mcp, get_gpu_info, exposed)

    async def step_frame() -> str:
        """Advance simulation exactly 1 frame (timeScale 0 -> 1 -> 0)."""
        return await call_fn("stepFrame")
    maybe_expose(mcp, step_frame, exposed, read_only=False)

    async def toggle_active(path: str) -> str:
        """Toggle GameObject active state by path. Returns 'activated'/'deactivated: <path>'."""
        return await call_fn("toggleActive", path)
    maybe_expose(mcp, toggle_active, exposed)

    async def move_camera(x: float, y: float, z: float) -> str:
        """Move editor camera (or Camera.main) to world position (x, y, z)."""
        return await call_fn("moveCamera", x, y, z)
    maybe_expose(mcp, move_camera, exposed)

    async def audit_build_size() -> str:
        """Full build size audit: scripts/images/audio grouped by type, sorted biggest first."""
        return await call_fn("auditBuildSize")
    maybe_expose(mcp, audit_build_size, exposed)

    async def audit_unused_modules() -> str:
        """Cross-reference loaded engine modules with active scene components. Flags unused modules."""
        return await call_fn("auditUnusedModules")
    maybe_expose(mcp, audit_unused_modules, exposed)

    async def audit_unused_assets() -> str:
        """Detect textures/audio/fonts loaded but not referenced by any component."""
        return await call_fn("auditUnusedAssets")
    maybe_expose(mcp, audit_unused_assets, exposed)

    async def get_build_recommendations() -> str:
        """Priority-ordered optimization tips combining all audits (size, modules, assets)."""
        return await call_fn("getBuildRecommendations")
    maybe_expose(mcp, get_build_recommendations, exposed)

    async def diagnose_bottlenecks() -> str:
        """Analyze runtime performance bottlenecks: FPS, draw calls, triangles, material switches,
        shaders, VRAM, memory, load time. Returns prioritized issues (CRITICAL > HIGH > MEDIUM)
        with specific fix recommendations. Use as first step when performance is poor."""
        return await call_fn("diagnoseBottlenecks")
    maybe_expose(mcp, diagnose_bottlenecks, exposed)

    async def get_animator_graph(path: str) -> str:
        """Full animator graph dump: layers, all states (name/normalizedTime/isLooping/speed), transitions, params."""
        return await call_fn("getAnimatorGraph", path)
    maybe_expose(mcp, get_animator_graph, exposed)

    async def get_luna_counters() -> str:
        """Luna performance counters from app.counters.previous: draw calls, vertices, particles, animators, UI elements. Dev-only counters labeled if advancedMode disabled."""
        return await call_fn("getLunaCounters")
    maybe_expose(mcp, get_luna_counters, exposed)

    async def inspect_environment() -> str:
        """Runtime environment info: Application, SystemInfo, Screen properties with per-property safety."""
        return await call_fn("getEnvironment")
    maybe_expose(mcp, inspect_environment, exposed)

    async def get_shader_variants() -> str:
        """Unity shader variant report: counts only (unityShaders, totalVariants, compiled, exported, missing, etc.)."""
        return await call_fn("getUnityShaderReport")
    maybe_expose(mcp, get_shader_variants, exposed)

    return {
        "get_performance_metrics": (get_performance_metrics, None),
        "diagnose_rendering": (diagnose_rendering, None),
        "audit_textures": (audit_textures, None),
        "get_render_stats": (get_render_stats, None),
        "get_vram_usage": (get_vram_usage, None),
        "get_gpu_info": (get_gpu_info, None),
        "step_frame": (step_frame, None),
        "toggle_active": (toggle_active, None),
        "move_camera": (move_camera, None),
        "audit_build_size": (audit_build_size, None),
        "audit_unused_modules": (audit_unused_modules, None),
        "audit_unused_assets": (audit_unused_assets, None),
        "get_build_recommendations": (get_build_recommendations, None),
        "diagnose_bottlenecks": (diagnose_bottlenecks, None),
        "get_animator_graph": (get_animator_graph, None),
        "get_luna_counters": (get_luna_counters, None),
        "inspect_environment": (inspect_environment, None),
        "get_shader_variants": (get_shader_variants, None),
    }
