"""Classify physics symptoms via keyword matching (Tier 1) then Haiku (Tier 2)."""
import re

CATEGORIES = ["jitter", "tunneling", "desync", "explosion", "sleep", "collision_miss", "general"]

KEYWORD_HINTS = {
    "jitter":          ["jiggle", "jiggl", "shake", "shak", "vibrate", "vibrat"],
    "tunneling":       ["fall through", "falls through", "passes through", "miss collision", "tunnel"],
    "desync":          ["desync", "out of sync", "stutter"],
    "explosion":       ["explode", "explod", "blow up", "stretch wildly"],
    "sleep":           ["sleep", "doesn't wake", "stuck", "frozen"],
    "collision_miss":  ["no collision", "missed collision", "raycast empty", "no hit"],
}


class SymptomClassifier:
    def __init__(self, sampling=None):
        self._sampling = sampling

    async def classify(self, symptom: str, backends: list) -> tuple:
        """Returns (category, confidence, keywords)."""
        if not symptom:
            return ("general", 0.0, [])
        sym_lower = symptom.lower()
        best_cat = "general"
        best_score = 0
        matched_kw: list = []
        for cat, hints in KEYWORD_HINTS.items():
            score = sum(1 for h in hints if re.search(re.escape(h), sym_lower))
            if score > best_score:
                best_score = score
                best_cat = cat
                matched_kw = [h for h in hints if re.search(re.escape(h), sym_lower)]
        if best_score > 0:
            return (best_cat, min(0.6 + 0.1 * best_score, 0.95), matched_kw)
        if self._sampling and self._sampling.enabled:
            prompt = (
                f"Classify physics symptom into ONE of: {','.join(CATEGORIES)}. "
                f"Backends active: {','.join(backends)}. "
                f"Symptom: '{symptom}'. Output: category,kw1,kw2"
            )
            try:
                result = await self._sampling.plan(prompt, "Concise classification.")
                if result:
                    parts = [p.strip() for p in result.strip().split(",")]
                    if parts and parts[0] in CATEGORIES:
                        return (parts[0], 0.7, parts[1:4])
            except Exception:
                pass
        return ("general", 0.3, [])
