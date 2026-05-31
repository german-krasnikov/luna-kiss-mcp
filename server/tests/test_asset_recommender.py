"""Tests for Recommender — RED phase."""
from __future__ import annotations
import pathlib
import pytest
from PIL import Image
from luna_mcp.asset_optimizer.catalog import Asset, AssetCatalog
from luna_mcp.asset_optimizer.texture_analyzer import TextureAnalyzer
from luna_mcp.asset_optimizer.recommender import Recommender, AssetAction

FIXTURES = pathlib.Path(__file__).parent / "fixtures" / "textures"


def _make_asset(path: str, abs_path: str, kind: str = "texture", size_bytes: int = 100_000) -> Asset:
    return Asset(path=path, abs_path=abs_path, kind=kind, size=size_bytes)


def test_action_dataclass():
    a = AssetAction("foo.png", "compress_jpeg", "reason", 50, "low")
    assert a.action == "compress_jpeg"
    assert a.est_save_kb == 50


def test_recommend_returns_list():
    r = Recommender(TextureAnalyzer())
    assets = [_make_asset("photo.png", str(FIXTURES / "photo_large.png"), size_bytes=200_000)]
    actions = r.recommend_textures(assets, target_size_kb=100)
    assert isinstance(actions, list)


def test_recommend_compress_photo():
    r = Recommender(TextureAnalyzer())
    assets = [_make_asset("photo.png", str(FIXTURES / "photo_large.png"), size_bytes=200_000)]
    actions = r.recommend_textures(assets, target_size_kb=100)
    assert len(actions) > 0
    assert actions[0].action == "compress_jpeg"


def test_recommend_compress_sprite():
    r = Recommender(TextureAnalyzer())
    assets = [_make_asset("sprite.png", str(FIXTURES / "sprite.png"), size_bytes=60_000)]
    actions = r.recommend_textures(assets, target_size_kb=50)
    assert len(actions) > 0
    assert actions[0].action == "compress_webp"


def test_skip_glyph_compression():
    r = Recommender(TextureAnalyzer())
    assets = [_make_asset("glyph.png", str(FIXTURES / "glyph_small.png"), size_bytes=5_000)]
    actions = r.recommend_textures(assets, target_size_kb=100)
    # glyphs should not be in the plan
    assert all(a.asset_path != "glyph.png" for a in actions)


def test_skip_non_texture_assets():
    r = Recommender(TextureAnalyzer())
    assets = [_make_asset("song.mp3", "/tmp/song.mp3", kind="audio", size_bytes=500_000)]
    actions = r.recommend_textures(assets, target_size_kb=100)
    assert len(actions) == 0


def test_target_size_caps_plan():
    r = Recommender(TextureAnalyzer())
    # Two large photos, target is small — should stop after first covers target
    assets = [
        _make_asset("photo1.png", str(FIXTURES / "photo_large.png"), size_bytes=500_000),
        _make_asset("photo2.png", str(FIXTURES / "photo_large.png"), size_bytes=500_000),
    ]
    actions = r.recommend_textures(assets, target_size_kb=1)
    assert len(actions) == 1  # first alone exceeds 1kb target


def test_sorted_by_est_save_desc():
    r = Recommender(TextureAnalyzer())
    assets = [
        _make_asset("small.png", str(FIXTURES / "photo_large.png"), size_bytes=100_000),
        _make_asset("big.png", str(FIXTURES / "photo_large.png"), size_bytes=500_000),
    ]
    actions = r.recommend_textures(assets, target_size_kb=10000)
    if len(actions) >= 2:
        assert actions[0].est_save_kb >= actions[1].est_save_kb


def test_risk_field_present():
    r = Recommender(TextureAnalyzer())
    assets = [_make_asset("photo.png", str(FIXTURES / "photo_large.png"), size_bytes=200_000)]
    actions = r.recommend_textures(assets, target_size_kb=100)
    assert actions[0].risk in ("low", "med", "high")
