"""RED: FlagRecommender — intent → flags."""
import pytest

from luna_mcp.flag_explorer.catalog import FlagCatalog
from luna_mcp.flag_explorer.recommender import FlagRecommender
from luna_mcp.flag_explorer.seeds import seed_default


@pytest.fixture
def recommender(tmp_path):
    catalog = FlagCatalog(tmp_path / "flags.json")
    seed_default(catalog)
    return FlagRecommender(catalog)


def test_recommend_returns_list(recommender):
    result = recommender.recommend("minify")
    assert isinstance(result, list)


def test_recommend_empty_intent_returns_empty(recommender):
    result = recommender.recommend("")
    assert result == []


def test_recommend_minify_finds_disableMinify(recommender):
    result = recommender.recommend("disable minification")
    names = [e.name for e in result]
    assert "disableMinify" in names


def test_recommend_texture_finds_texture_flags(recommender):
    result = recommender.recommend("texture compression quality")
    names = [e.name for e in result]
    assert any("exture" in n for n in names)


def test_recommend_console_logging_finds_flag(recommender):
    result = recommender.recommend("verbose logging console")
    names = [e.name for e in result]
    assert "enableConsoleLogging" in names


def test_recommend_respects_max_results(recommender):
    # seed has 5 entries; broad keyword "size" may match several
    result = recommender.recommend("texture size build performance logging solver", max_results=2)
    assert len(result) <= 2


def test_recommend_no_match_returns_empty(recommender):
    result = recommender.recommend("xyzzy foobarbaz")
    assert result == []


def test_recommend_physics_finds_unstable_solver(recommender):
    result = recommender.recommend("physics solver performance")
    names = [e.name for e in result]
    assert "useUnstableSolver" in names
