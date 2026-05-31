"""PhysicsKnowledge — facade over LessonStore for physics_* pattern_kinds."""
import re
from typing import Optional


class PhysicsKnowledge:
    def __init__(self, store: Optional[object]):
        self._store = store

    def query(self, backend: str, symptom: str, build_hash: str = "*") -> list:
        """Find physics lessons matching backend + symptom keywords. Returns up to 3."""
        if not self._store:
            return []
        pattern_kind = f"physics_{backend}"
        all_lessons = self._store.find_by_kind(cmd="diagnose_physics", pattern_kind=pattern_kind)
        sym_lower = (symptom or "").lower()
        out = []
        for L in all_lessons:
            keywords = [k.strip() for k in L.situation.split("|")]
            if any(re.search(re.escape(kw.lower()), sym_lower) for kw in keywords if kw):
                out.append(L)
        return out[:3]
