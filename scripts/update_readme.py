#!/usr/bin/env python3
"""Extract live metrics from the codebase and patch README.md + SVG assets.

Runs locally or in CI. When env vars (TEST_COUNT, EXPOSED_TOOLS, …) are set
they override auto-detection — handy for the GitHub Action that already
computed everything.

Usage:
    python3 scripts/update_readme.py          # auto-detect from codebase
    TEST_COUNT=1940 python3 scripts/update_readme.py  # override one metric
"""
from __future__ import annotations

import os
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SERVER = ROOT / "server"
README = ROOT / "README.md"
CHANGELOG = ROOT / "CHANGELOG.md"
HERO_SVG = ROOT / ".github" / "assets" / "hero.svg"
SUBTITLE_SVG = ROOT / ".github" / "assets" / "subtitle.svg"
CHANGELOG_SVG = ROOT / ".github" / "assets" / "changelog.svg"


# ---------------------------------------------------------------------------
# Metric extraction (fallbacks when env vars are not set)
# ---------------------------------------------------------------------------

def _run(cmd: str, cwd: Path | None = None) -> str:
    r = subprocess.run(cmd, shell=True, capture_output=True, text=True, cwd=cwd)
    return r.stdout.strip()


def _count_exposed_tools() -> int:
    wiring = (SERVER / "src" / "luna_mcp" / "wiring.py").read_text()
    m = re.search(r"EXPOSED_TOOLS:\s*set\[str\]\s*=\s*\{(.+?)\}", wiring, re.DOTALL)
    if not m:
        return 0
    raw = re.sub(r"#[^\n]*", "", m.group(1))
    return len([t for t in re.findall(r'"([^"]+)"', raw) if t])


def _count_total_tools() -> int:
    total = 0
    tools_dir = SERVER / "src" / "luna_mcp" / "tools"
    extra = [SERVER / "src" / "luna_mcp" / "regression" / "tools.py"]
    for p in list(tools_dir.glob("*.py")) + extra:
        if p.name == "__init__.py" or not p.exists():
            continue
        total += len(re.findall(r'"(\w+)":\s*\(', p.read_text()))
    return total


def _count_tests() -> tuple[int, int]:
    """Return (test_count, test_file_count)."""
    r = subprocess.run(
        ["python3", "-m", "pytest", "tests/", "--collect-only", "-q"],
        capture_output=True, text=True, cwd=SERVER, timeout=120,
    )
    count = 0
    for line in r.stdout.splitlines()[-5:]:
        m = re.search(r"(\d+)\s+tests?\s", line)
        if m:
            count = int(m.group(1))
    files = len(list((SERVER / "tests").rglob("test_*.py")))
    return count, files


def _count_loc() -> tuple[int, int]:
    """Return (python_loc, js_loc)."""
    py = 0
    for p in (SERVER / "src").rglob("*.py"):
        py += sum(1 for ln in p.read_text().splitlines() if ln.strip() and not ln.strip().startswith("#"))
    for p in (SERVER / "tests").rglob("*.py"):
        py += sum(1 for ln in p.read_text().splitlines() if ln.strip() and not ln.strip().startswith("#"))
    js_file = ROOT / "js" / "luna_helpers.js"
    js = 0
    if js_file.exists():
        js = sum(1 for ln in js_file.read_text().splitlines() if ln.strip() and not ln.strip().startswith("//"))
    return py, js


def _git_commit_count() -> int:
    out = _run("git rev-list --count HEAD", cwd=ROOT)
    return int(out) if out.isdigit() else 0


def _detect_version() -> str:
    cl = CHANGELOG.read_text() if CHANGELOG.exists() else ""
    m = re.search(r"##\s*\[(\d+\.\d+\.\d+)\]", cl)
    return m.group(1) if m else "0.1.0"


def get_metrics() -> dict[str, str]:
    """Build the metrics dict, preferring env vars over auto-detection."""
    exposed = int(os.environ.get("EXPOSED_TOOLS") or _count_exposed_tools())
    total = int(os.environ.get("TOTAL_TOOLS") or _count_total_tools())
    batch = total - exposed

    if os.environ.get("TEST_COUNT"):
        tests, test_files = int(os.environ["TEST_COUNT"]), int(os.environ.get("TEST_FILES", 0))
    else:
        tests, test_files = _count_tests()

    if os.environ.get("PY_LOC"):
        py_loc, js_loc = int(os.environ["PY_LOC"]), int(os.environ.get("JS_LOC", 0))
    else:
        py_loc, js_loc = _count_loc()

    commits = int(os.environ.get("COMMIT_COUNT") or _git_commit_count())
    version = os.environ.get("VERSION") or _detect_version()

    return {
        "TOOLS_TOTAL": str(total),
        "TOOLS_EXPOSED": str(exposed),
        "TOOLS_BATCH": str(batch),
        "TEST_COUNT": str(tests),
        "TEST_FILES": str(test_files),
        "PY_LOC": f"{py_loc:,}",
        "JS_LOC": f"{js_loc:,}",
        "TOTAL_LOC": f"{py_loc + js_loc:,}",
        "COMMITS": str(commits),
        "VERSION": version,
    }


# ---------------------------------------------------------------------------
# Replacement engines
# ---------------------------------------------------------------------------

def _replace_badge(text: str, label: str, new_val: str) -> str:
    """Update shields.io badge: badge/label-VALUE-color."""
    return re.sub(
        rf"(badge/{re.escape(label)}-)[\w%.]+(-)",
        rf"\g<1>{new_val}\2",
        text,
    )


def _replace_prose(text: str, old_num: str, new_num: str, suffix: str) -> str:
    """Replace e.g. '1936 tests' -> '1940 tests' everywhere."""
    return re.sub(rf"\b{re.escape(old_num)}\s+{re.escape(suffix)}", f"{new_num} {suffix}", text)


# The old hardcoded values we're replacing (from the current README)
OLD = {
    "tools_total": "149",
    "tools_exposed": "112",
    "tools_batch": "37",
    "tests": "1936",
    "test_files": "147",
    "loc": "23,779",
}


def update_readme(m: dict[str, str]) -> None:
    text = README.read_text()

    for old, new, suffix in [
        (OLD["tools_total"], m["TOOLS_TOTAL"], "tools"),
        (OLD["tools_total"], m["TOOLS_TOTAL"], "total tools"),
        (OLD["tools_total"], m["TOOLS_TOTAL"], "total"),
        (OLD["tools_exposed"], m["TOOLS_EXPOSED"], "AI-exposed"),
        (OLD["tools_batch"], m["TOOLS_BATCH"], "batch-only"),
        (OLD["tests"], m["TEST_COUNT"], "tests"),
        (OLD["test_files"], m["TEST_FILES"], "files"),
        (OLD["test_files"], m["TEST_FILES"], "test files"),
    ]:
        text = _replace_prose(text, old, new, suffix)

    # LOC with comma: ~23,779 -> ~N
    text = text.replace(f"~{OLD['loc']}", f"~{m['TOTAL_LOC']}")
    text = text.replace(OLD["loc"], m["TOTAL_LOC"])

    # "1,936 tests" variant
    text = text.replace(f"1,936 tests", f"{int(m['TEST_COUNT']):,} tests")

    # Badge numbers
    text = _replace_badge(text, "tests", f"{m['TEST_COUNT']}%20passing")
    text = _replace_badge(text, "tools", m["TOOLS_TOTAL"])

    # Version badge
    text = re.sub(
        r"(badge/[Ss]tatus-)[Bb]eta%20v[\d.]+",
        rf"\g<1>Beta%20v{m['VERSION']}",
        text,
    )
    text = re.sub(
        r"(badge/v)[\d.]+-beta",
        rf"\g<1>{m['VERSION']}-beta",
        text,
    )

    # Inline version mentions
    text = re.sub(r"Beta \(v[\d.]+\)", f"Beta (v{m['VERSION']})", text)
    text = re.sub(r"beta v[\d.]+", f"beta v{m['VERSION']}", text, flags=re.IGNORECASE)

    README.write_text(text)
    print(f"  README.md  -> {m['TOOLS_TOTAL']} tools, {m['TEST_COUNT']} tests, {m['TOTAL_LOC']} LOC, v{m['VERSION']}")


def update_svg(path: Path, replacements: list[tuple[str, str]], label: str) -> None:
    if not path.exists():
        print(f"  {label}: SKIP (not found)")
        return
    text = path.read_text()
    for old, new in replacements:
        text = text.replace(old, new)
    path.write_text(text)
    print(f"  {label}: updated")


def update_hero(m: dict[str, str]) -> None:
    if not HERO_SVG.exists():
        return
    text = HERO_SVG.read_text()
    # <tspan fill="#39E0FF" font-weight="700">149</tspan><tspan fill="#C2C9DD"> tools</tspan>
    text = re.sub(
        r'(<tspan fill="#39E0FF" font-weight="700">)\d+(</tspan><tspan fill="#C2C9DD"> tools)',
        rf"\g<1>{m['TOOLS_TOTAL']}\2",
        text,
    )
    text = re.sub(
        r'(<tspan fill="#8B7DFF" font-weight="700">)\d+(</tspan><tspan fill="#C2C9DD"> tests)',
        rf"\g<1>{m['TEST_COUNT']}\2",
        text,
    )
    HERO_SVG.write_text(text)
    print(f"  hero.svg   -> {m['TOOLS_TOTAL']} tools, {m['TEST_COUNT']} tests")


def update_subtitle(m: dict[str, str]) -> None:
    if not SUBTITLE_SVG.exists():
        return
    text = SUBTITLE_SVG.read_text()
    text = re.sub(r"\d+ tools over CDP", f"{m['TOOLS_TOTAL']} tools over CDP", text)
    # aria-label
    text = re.sub(r"\d+ tools over CDP", f"{m['TOOLS_TOTAL']} tools over CDP", text)
    SUBTITLE_SVG.write_text(text)
    print(f"  subtitle   -> {m['TOOLS_TOTAL']} tools")


def update_changelog_svg(m: dict[str, str]) -> None:
    if not CHANGELOG_SVG.exists():
        return
    text = CHANGELOG_SVG.read_text()
    # desc + stat texts
    text = re.sub(r'font-weight="700" fill="#E8ECF6">\d+', f'font-weight="700" fill="#E8ECF6">{m["TOOLS_TOTAL"]}', text)
    text = re.sub(r'font-weight="700" fill="#39E0FF">\d+', f'font-weight="700" fill="#39E0FF">{m["TEST_COUNT"]}', text)
    text = re.sub(r'font-weight="700" fill="#6AB6FF">[\d,]+', f'font-weight="700" fill="#6AB6FF">{m["TOTAL_LOC"]}', text)
    text = re.sub(r"tools \d+ AI \+ \d+", f"tools {m['TOOLS_EXPOSED']} AI + {m['TOOLS_BATCH']}", text)
    text = re.sub(r"tests / \d+ files", f"tests / {m['TEST_FILES']} files", text)
    # desc tag
    text = re.sub(r"\d+ tools,\s*\d+ tests,\s*and [\d,]+ LOC",
                  f"{m['TOOLS_TOTAL']} tools, {m['TEST_COUNT']} tests, and {m['TOTAL_LOC']} LOC", text)
    CHANGELOG_SVG.write_text(text)
    print(f"  changelog  -> {m['TOOLS_TOTAL']} tools, {m['TEST_COUNT']} tests, {m['TOTAL_LOC']} LOC")


def update_generic_svgs(m: dict[str, str]) -> None:
    """Patch tool/test counts in all remaining SVG assets."""
    assets = ROOT / ".github" / "assets"
    for svg_path in assets.glob("*.svg"):
        text = svg_path.read_text()
        original = text
        text = re.sub(r"\b149 tools\b", f"{m['TOOLS_TOTAL']} tools", text)
        text = re.sub(r"\b1936 tests\b", f"{m['TEST_COUNT']} tests", text)
        text = re.sub(r"\b1,936 tests\b", f"{int(m['TEST_COUNT']):,} tests" if m['TEST_COUNT'].isdigit() else text, text)
        if text != original:
            svg_path.write_text(text)
            print(f"  {svg_path.name}: patched")


def main() -> None:
    print("Extracting metrics...")
    m = get_metrics()
    for k, v in sorted(m.items()):
        print(f"  {k}: {v}")
    print("\nPatching files...")
    update_readme(m)
    update_hero(m)
    update_subtitle(m)
    update_changelog_svg(m)
    update_generic_svgs(m)
    print("\nDone.")


if __name__ == "__main__":
    main()
