"""F11 Smart Error Triage — Tier 1 dedup + classify, Tier 2 optional Haiku summary."""
import hashlib
import re
from collections import Counter, OrderedDict

_CRITICAL_RE = re.compile(r'NullRef|Exception|Error|FATAL|Uncaught', re.I)
_NOISE_RE = re.compile(r'DOTween|Canvas|Layout|deprecated|obsolete', re.I)

_ORDER = {"critical": 0, "info": 1, "noise": 2}


def _fingerprint(line: str) -> str:
    return hashlib.sha256(line[:80].encode()).hexdigest()[:12]


def _classify(line: str) -> str:
    if _CRITICAL_RE.search(line):
        return "critical"
    if _NOISE_RE.search(line):
        return "noise"
    return "info"


def triage(raw: str) -> dict:
    """Tier 1: dedup + classify. Returns groups + stats."""
    lines = [l for l in raw.splitlines() if l.strip()]
    fp_count: Counter = Counter(_fingerprint(l) for l in lines)
    dupes = sum(c - 1 for c in fp_count.values())

    seen: OrderedDict = OrderedDict()
    for line in lines:
        fp = _fingerprint(line)
        if fp not in seen:
            seen[fp] = {"severity": _classify(line), "count": fp_count[fp], "sample": line}

    groups = sorted(seen.values(), key=lambda g: _ORDER[g["severity"]])
    stats = {"dupes": dupes, "critical": 0, "noise": 0, "info": 0}
    for g in groups:
        stats[g["severity"]] += g["count"]

    return {"groups": groups, "stats": stats}


def _format_tier1(result: dict) -> str:
    s = result["stats"]
    if not result["groups"]:
        return "No errors"
    header = f"{s['critical']} critical, {s['noise']} noise, {s['dupes']} dupes"
    lines = [header, "", "[TOP ERRORS]"]
    for g in result["groups"][:10]:
        prefix = f"[{g['severity'].upper()}]"
        count = f"×{g['count']}" if g["count"] > 1 else ""
        lines.append(f"  {prefix} {count} {g['sample']}")
    return "\n".join(lines)


async def triage_with_llm(raw: str, sampling) -> str:
    """Tier 1 + optional Tier 2 Haiku summary."""
    result = triage(raw)
    tier1 = _format_tier1(result)
    if not result["groups"] or sampling is None:
        return tier1
    unique_samples = "\n".join(g["sample"] for g in result["groups"][:20])
    prompt = (
        f"Summarize these unique console errors into actionable 1-liners, grouped by root cause:\n{unique_samples}"
    )
    summary = await sampling.plan(prompt, "Summarize console errors grouped by root cause.")
    if not summary:
        return tier1
    return f"{tier1}\n\n[LLM SUMMARY]\n{summary}"
