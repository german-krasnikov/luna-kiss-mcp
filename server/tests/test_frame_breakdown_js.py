"""Tests for F4 getFrameBreakdown folded into getPerformanceMetrics (JS-only)."""
import pathlib

JS_PATH = pathlib.Path(__file__).parent.parent.parent / "js" / "luna_helpers.js"


def _js():
    return JS_PATH.read_text()


def test_frame_breakdown_string_present():
    assert 'frameBreakdown' in _js()


def test_counters_previous_guard():
    """Must use .previous (last completed frame), not .current."""
    js = _js()
    assert 'counters' in js
    assert '.previous' in js


def test_frame_breakdown_keys_present():
    """All breakdown keys must be present."""
    js = _js()
    for key in ('render', 'scripts', 'animations', 'physics'):
        assert key in js
