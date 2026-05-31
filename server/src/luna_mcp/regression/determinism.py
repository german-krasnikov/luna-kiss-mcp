"""Determinism helpers: seed PRNG + wait for 3 rAF frames."""

_SEED_JS = """
(function(s){{
  if (!window.__luna_seeded) {{
    Math.random = function() {{
      s |= 0; s = s + 0x6D2B79F5 | 0;
      var t = Math.imul(s ^ s >>> 15, 1 | s);
      t = t + Math.imul(t ^ t >>> 7, 61 | t) ^ t;
      return ((t ^ t >>> 14) >>> 0) / 4294967296;
    }};
    window.__luna_seeded = s;
  }}
  return 'seeded ' + window.__luna_seeded;
}})({seed})
"""

_RAF3_JS = (
    "new Promise(r => requestAnimationFrame("
    "()=>requestAnimationFrame(()=>requestAnimationFrame(r))))"
)


async def prepare_deterministic(bridge, seed: int = 42) -> None:
    """Seed Math.random and wait 3 animation frames for stable rendering."""
    await bridge.eval(_SEED_JS.format(seed=seed))
    try:
        await bridge.eval(_RAF3_JS)
    except Exception:
        pass  # rAF may not be available in test env
