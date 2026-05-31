"""Static build helper functions — no Chrome needed."""
from __future__ import annotations

import json
from pathlib import Path


def stage4(build_path: str) -> Path:
    return Path(build_path) / "LunaTemp" / "stage4" / "develop"


def stage3(build_path: str) -> Path:
    return Path(build_path) / "LunaTemp" / "stage3"


def read_json(p: Path) -> dict | list | None:
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return None


def walk_sizes(root: Path) -> dict[str, int]:
    """Return {ext: total_bytes} for all files under root."""
    totals: dict[str, int] = {}
    if not root.exists():
        return totals
    for f in root.rglob("*"):
        if f.is_file():
            ext = f.suffix.lower() or ".other"
            totals[ext] = totals.get(ext, 0) + f.stat().st_size
    return totals


def biggest_files(root: Path, ext: str, n: int = 5) -> list[tuple[str, int]]:
    """Return top-n (name, size) for files with given extension."""
    files = []
    if not root.exists():
        return files
    for f in root.rglob(f"*{ext}"):
        if f.is_file():
            files.append((f.name, f.stat().st_size))
    return sorted(files, key=lambda x: -x[1])[:n]


def fmt_kb(b: int) -> str:
    kb = b // 1024
    if kb >= 1024:
        return f"{kb/1024:.1f} MB"
    return f"{kb} KB"


def fmt_playground(fields_map: dict) -> list[str]:
    lines = []
    for cls, fields in fields_map.items():
        for fname, meta in fields.items():
            t = meta.get("type", "?")
            default = meta.get("defaultValue", "")
            title = meta.get("title", "")
            section = meta.get("section", "")
            sec_tag = f" [{section}]" if section else ""
            lines.append(f"  {fname} ({t}): {default} — {title}{sec_tag}")
    return lines


def recommendations(js_files: list[tuple[str, int]], tex_files: list[tuple[str, int]], shader_count: int) -> list[str]:
    recs = []
    for name, size in js_files:
        kb = size // 1024
        if "TextMeshPro" in name:
            recs.append(f"[CRITICAL] {name} ({kb}KB) — check if TMP components used at runtime")
        elif "physics2d" in name.lower():
            recs.append(f"[CRITICAL] {name} ({kb}KB) — check if 2D physics used at runtime")
    for name, size in tex_files:
        kb = size // 1024
        if "LiberationSans" in name:
            recs.append(f"[WARNING] {name} ({kb}KB) — TMP font asset, remove if TMP not used")
        elif "EmojiOne" in name:
            recs.append(f"[WARNING] {name} ({kb}KB) — TMP sprite asset")
    if shader_count > 50:
        recs.append(f"[INFO] {shader_count} shaders compiled — verify all needed at runtime with get_shader_report")
    return recs
