"""BrainScanner: Haiku-powered anomaly detection for Luna runtime."""
import hashlib
import re
import time

_SYS = (
    "Analyze console errors + performance metrics for a Unity-to-JS playable ad. "
    "Detect: memory leaks (rising heap), particle infinite loops, shader fallbacks, "
    "performance regressions. Output max 3 findings, one per line. "
    "Format: SEVERITY: description. If nothing abnormal: 'OK'"
)

_FPS_RE = re.compile(r"fps[:\s]+(\d+(?:\.\d+)?)", re.IGNORECASE)
_DC_RE = re.compile(r"draw\s*calls?[:\s]+(\d+)", re.IGNORECASE)
_HEAP_RE = re.compile(r"heap[:\s]+(\d+(?:\.\d+)?)\s*mb", re.IGNORECASE)


class BrainScanner:
    def __init__(self):
        self._last_scan = float("-inf")
        self._debounce = 60.0
        self._seen: dict = {}
        self._anomalies: list = []

    @property
    def anomalies(self) -> list:
        return self._anomalies

    async def analyze(self, console_text: str, perf_text: str, sampling) -> list:
        now = time.monotonic()
        if now - self._last_scan < self._debounce:
            return self._anomalies
        if not sampling or not sampling.enabled:
            return self._check_thresholds(perf_text)
        self._last_scan = now
        combined = f"CONSOLE:\n{console_text}\n\nPERFORMANCE:\n{perf_text}"
        result = await sampling.plan(combined, _SYS)
        if not result or result.strip() == "OK":
            self._anomalies = []
            return []
        findings = [l.strip() for l in result.strip().split("\n")
                    if l.strip() and l.strip() != "OK"]
        new_findings = []
        for f in findings:
            fp = hashlib.sha256(f[:60].encode()).hexdigest()[:12]
            if fp not in self._seen or now - self._seen[fp] > self._debounce:
                self._seen[fp] = now
                new_findings.append(f)
        self._anomalies = new_findings
        return new_findings

    def _check_thresholds(self, perf_text: str) -> list:
        issues = []
        m = _FPS_RE.search(perf_text)
        if m and float(m.group(1)) < 20:
            issues.append(f"LOW_FPS: {m.group(1)} FPS detected")
        m = _DC_RE.search(perf_text)
        if m and int(m.group(1)) > 200:
            issues.append(f"HIGH_DRAWCALLS: {m.group(1)} draw calls")
        m = _HEAP_RE.search(perf_text)
        if m and float(m.group(1)) > 200:
            issues.append(f"HIGH_MEMORY: {m.group(1)}MB heap usage")
        return issues
