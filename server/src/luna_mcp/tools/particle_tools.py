"""F5: audit_particles tool — passthrough to particleAudit JS helper."""
from . import maybe_expose


def register_particle_tools(mcp, call_fn, *, exposed: set = frozenset()):
    async def audit_particles() -> str:
        """Audit particle systems: alive count, max, play/emit state, rate. Sorted by alive ratio."""
        return await call_fn("particleAudit")

    maybe_expose(mcp, audit_particles, exposed, read_only=True)
    return {"audit_particles": (audit_particles, None)}
