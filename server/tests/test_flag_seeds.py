"""RED: FlagSeeds — 4 starter entries (compressTexturesWebP removed), idempotent seeding."""
import pytest

from luna_mcp.flag_explorer.catalog import FlagCatalog
from luna_mcp.flag_explorer.seeds import SEED_FLAGS, seed_default


@pytest.fixture
def catalog(tmp_path):
    return FlagCatalog(tmp_path / "flags.json")


def test_seed_flags_count():
    assert len(SEED_FLAGS) == 4


def test_seed_flags_names():
    names = {e.name for e in SEED_FLAGS}
    assert "disableMinify" in names
    assert "forceUncompressedTextures" in names
    assert "useUnstableSolver" in names
    assert "enableConsoleLogging" in names
    assert "compressTexturesWebP" not in names


def test_no_unverified_seed():
    assert all(s.source != "seed_hypothetical" for s in SEED_FLAGS)
    assert "compressTexturesWebP" not in {s.name for s in SEED_FLAGS}


def test_seed_default_adds_four(catalog):
    n = seed_default(catalog)
    assert n == 4


def test_seed_default_idempotent(catalog):
    seed_default(catalog)
    n2 = seed_default(catalog)
    assert n2 == 0


def test_seed_default_saves(catalog, tmp_path):
    seed_default(catalog)
    path = tmp_path / "flags.json"
    assert path.exists()


def test_seed_entries_have_source_seed(catalog):
    seed_default(catalog)
    for e in catalog.all():
        assert e.source.startswith("seed")


def test_seed_entries_have_descriptions(catalog):
    seed_default(catalog)
    for e in catalog.all():
        assert len(e.description) > 5


def test_seed_entries_have_risk(catalog):
    seed_default(catalog)
    risks = {e.risk for e in catalog.all()}
    assert risks <= {"low", "medium", "high"}


def test_seed_entries_have_confidence(catalog):
    seed_default(catalog)
    for e in catalog.all():
        assert 0 < e.confidence <= 1.0


def test_seed_disable_minify_risk_low(catalog):
    seed_default(catalog)
    e = catalog.get("disableMinify")
    assert e is not None
    assert e.risk == "low"


def test_seed_unstable_solver_risk_high(catalog):
    seed_default(catalog)
    e = catalog.get("useUnstableSolver")
    assert e is not None
    assert e.risk == "high"
