"""BuildIndex: walk a build directory → Manifest with file metadata."""
from __future__ import annotations

import hashlib
import pathlib
import re
import time
from dataclasses import dataclass

# Strip known timestamp patterns before hashing text files for determinism
_TS_RE = re.compile(
    r'/\*\s*\d{10,}\s*\*/'
    r'|//\s*\d{10,}'
    r'|"(?:timestamp|buildTime|generatedAt|compiledAt|builtAt|builtOn|createdAt|updatedAt)"\s*:\s*\d+'
    r'|"(?:timestamp|buildTime|generatedAt|compiledAt|builtAt|builtOn|createdAt|updatedAt)"\s*:\s*"[^"]*"',
    re.MULTILINE,
)

_TEXT_KINDS = frozenset({"js", "json", "css", "html", "txt"})
_KIND_BY_EXT = {
    ".js": "js", ".json": "json", ".css": "css", ".html": "html",
    ".png": "png", ".jpg": "png", ".webp": "png",
    ".wasm": "wasm", ".txt": "txt",
}


@dataclass(frozen=True)
class FileEntry:
    path: str       # relative to build root
    size: int
    sha256: str     # 16-char hex, normalized
    kind: str       # js|json|png|wasm|asset|other


@dataclass
class Manifest:
    label: str
    root: str       # absolute path
    total_size: int
    files: list
    created_at: float


class BuildIndex:
    @staticmethod
    def classify(path: pathlib.Path) -> str:
        return _KIND_BY_EXT.get(path.suffix.lower(), "other")

    @staticmethod
    def hash_file(path: pathlib.Path, kind: str) -> str:
        """Normalized hash: text strips timestamps, binary raw. Returns 16-char hex."""
        try:
            if kind in _TEXT_KINDS:
                content = path.read_text(errors="replace")
                content = _TS_RE.sub("", content)
                return hashlib.sha256(content.encode()).hexdigest()[:16]
            return hashlib.sha256(path.read_bytes()).hexdigest()[:16]
        except Exception:
            return f"ERR:{hashlib.sha256(str(path).encode()).hexdigest()[:12]}"

    @classmethod
    def scan(cls, root: pathlib.Path, label: str) -> Manifest:
        root = pathlib.Path(root).resolve()
        if not root.exists() or not root.is_dir():
            raise ValueError(f"not a directory: {root}")
        files = []
        total = 0
        for p in root.rglob("*"):
            if not p.is_file():
                continue
            rel_parts = p.relative_to(root).parts
            if any(part.startswith(".") for part in rel_parts):
                continue
            try:
                size = p.stat().st_size
                rel = str(p.relative_to(root))
                kind = cls.classify(p)
                files.append(FileEntry(path=rel, size=size, sha256=cls.hash_file(p, kind), kind=kind))
                total += size
            except (OSError, ValueError):
                continue
        return Manifest(
            label=label,
            root=str(root),
            total_size=total,
            files=sorted(files, key=lambda f: f.path),
            created_at=time.time(),
        )
