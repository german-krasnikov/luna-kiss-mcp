"""Detect active physics backend by probing the Luna JS runtime."""
import re


class BackendInfo:
    def __init__(self, raw: str):
        self.raw = raw
        self.goblin = "goblin=true" in raw
        self.verlet = "verlet=true" in raw
        self.baked = "baked=true" in raw
        self.unified = "unified=true" in raw
        m = re.search(r'goblin\.bodies=(\d+)', raw)
        self.goblin_bodies = int(m.group(1)) if m else 0
        m = re.search(r'verlet\.particles=(\d+)', raw)
        self.verlet_particles = int(m.group(1)) if m else 0
        m = re.search(r'baked\.entries=(\d+)', raw)
        self.baked_entries = int(m.group(1)) if m else 0

    def active_backends(self) -> list:
        out = []
        if self.goblin:
            out.append("goblin")
        if self.verlet:
            out.append("verlet")
        if self.baked:
            out.append("baked")
        if self.unified:
            out.append("unified")
        return out

    def summary(self) -> str:
        backends = self.active_backends()
        if not backends:
            return "no physics detected"
        parts = [f"backends={','.join(backends)}"]
        if self.goblin:
            parts.append(f"goblin.bodies={self.goblin_bodies}")
        if self.verlet:
            parts.append(f"verlet.particles={self.verlet_particles}")
        if self.baked:
            parts.append(f"baked.entries={self.baked_entries}")
        return " ".join(parts)


async def detect_backend(call_fn) -> BackendInfo:
    """Invoke physicsProbe JS helper. Returns BackendInfo."""
    try:
        raw = await call_fn("physicsProbe")
    except Exception as e:
        return BackendInfo(f"error: {e}")
    return BackendInfo(str(raw or ""))
