"""Haiku planner: intent → PatchOp DSL via SamplingService."""
import re
from typing import Optional

_PROMPT_HEAD = """\
You are a Luna jakefile patching planner. Convert intent → PatchOp DSL.
Output ONLY commands, one per line. Format:
  PATCH id=<id> search=<exact_string> replace=<new_string> count=<N> [anchor_before=<str>] [anchor_after=<str>]

Use ONLY anchor strings from this index (these survive obfuscation):
{anchors}

Available task hooks: {tasks}

RULES:
- Each search MUST be an exact substring of the jakefile (use anchor strings as guidance).
- Provide EITHER anchor_before OR anchor_after for each PATCH.
- Maximum 5 PATCH lines.
- NO prose, NO markdown fences."""

_PATCH_RE = re.compile(r"^\s*PATCH\s+(.*)$")
# Tokenize key=value where value is either quoted OR runs until the next word= or EOL
_KV_RE = re.compile(r'(\w+)=("[^"]+"|\'[^\']+\'|(?:(?!\s+\w+=).)+)')


class JakefilePlanner:
    def __init__(self, sampling):
        self._sampling = sampling

    async def plan(self, intent: str, index, ctx: str = "") -> Optional[str]:
        if self._sampling is None or not self._sampling.enabled:
            return None
        prompt = _PROMPT_HEAD.format(
            anchors="\n".join(f"- {a}" for a in index.anchors[:30]),
            tasks=", ".join(index.task_names[:25]),
        )
        try:
            return await self._sampling.plan(intent, prompt, ctx)
        except Exception:
            return None


def parse_dsl(text: str) -> list:
    if not text:
        return []
    out = []
    for line in text.split("\n"):
        m = _PATCH_RE.match(line)
        if not m:
            continue
        kwargs: dict = {}
        for k, v in _KV_RE.findall(m.group(1)):
            if (v.startswith('"') and v.endswith('"')) or (v.startswith("'") and v.endswith("'")):
                v = v[1:-1]
            if k == "count":
                try:
                    v = int(v)
                except ValueError:
                    continue  # drop malformed count; caller falls back to expected_count=1
            kwargs[k] = v
        if "id" in kwargs and "search" in kwargs and "replace" in kwargs:
            out.append(kwargs)
    return out[:5]
