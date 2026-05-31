"""Chunked Haiku diff for text files."""
from __future__ import annotations

import difflib
import pathlib
from typing import Optional

CHUNK_SIZE = 8000  # chars


class SemanticDiff:
    def __init__(self, sampling):
        self._sampling = sampling

    async def diff_text_file(
        self, path_a: pathlib.Path, path_b: pathlib.Path, file_path: str
    ) -> Optional[str]:
        """Returns 1-line summary or None if identical/disabled/error."""
        if self._sampling is None or not self._sampling.enabled:
            return None
        try:
            a_lines = path_a.read_text(errors="replace").splitlines(keepends=True)
            b_lines = path_b.read_text(errors="replace").splitlines(keepends=True)
        except Exception as e:
            return f"read error: {e}"
        diff = list(difflib.unified_diff(a_lines, b_lines, fromfile="a", tofile="b", n=2))
        if not diff:
            return None
        diff_text = "".join(diff)
        if len(diff_text) <= CHUNK_SIZE:
            return await self._summarize_chunk(diff_text, file_path)
        s = await self._summarize_chunk(diff_text[:CHUNK_SIZE], file_path)
        if s:
            return f"{s} (truncated diff: {len(diff_text)} total chars)"
        return f"large diff ({len(diff_text)} chars, summarization failed)"

    async def _summarize_chunk(self, diff_text: str, file_path: str) -> Optional[str]:
        prompt = (
            f"Diff for {file_path}. Summarize what changed in ≤120 chars. "
            f"Focus on semantic intent, not syntax.\n\n{diff_text}"
        )
        try:
            return await self._sampling.plan(prompt, "Concise diff summarizer.")
        except Exception:
            return None
