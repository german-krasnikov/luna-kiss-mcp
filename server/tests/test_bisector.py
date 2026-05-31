"""Tests for build_diff/bisector.py — RED phase."""
import pytest

from luna_mcp.build_diff.bisector import Bisector


@pytest.mark.asyncio
async def test_bisect_no_intermediates_returns_bad():
    async def probe(label):
        return True
    b = Bisector(probe)
    culprit, probes = await b.find_culprit("good", "bad", [])
    assert culprit == "bad"
    assert probes == 0


@pytest.mark.asyncio
async def test_bisect_single_intermediate_bad():
    async def probe(label):
        return label == "good"  # v0 is bad
    b = Bisector(probe)
    culprit, probes = await b.find_culprit("good", "bad", ["v0"])
    assert culprit == "v0"
    assert probes == 1


@pytest.mark.asyncio
async def test_bisect_single_intermediate_good():
    async def probe(label):
        return label != "bad"  # only "bad" is bad
    b = Bisector(probe)
    culprit, probes = await b.find_culprit("good", "bad", ["v0"])
    assert culprit == "bad"
    assert probes == 1


@pytest.mark.asyncio
async def test_bisect_3_probes_for_8_intermediates():
    """log2(8) = 3 probes — culprit at v5."""
    intermediates = [f"v{i}" for i in range(8)]

    async def probe(label):
        if label == "good":
            return True
        if label == "bad":
            return False
        return int(label[1:]) < 5  # v0..v4 good, v5..v7 bad

    b = Bisector(probe)
    culprit, probes = await b.find_culprit("good", "bad", intermediates)
    assert culprit == "v5"
    assert probes <= 4  # log2(10) ≈ 3.3


@pytest.mark.asyncio
async def test_bisect_culprit_at_start():
    """First intermediate is already bad."""
    async def probe(label):
        return label == "good"

    b = Bisector(probe)
    intermediates = [f"v{i}" for i in range(4)]
    culprit, probes = await b.find_culprit("good", "bad", intermediates)
    assert culprit == "v0"


@pytest.mark.asyncio
async def test_bisect_culprit_at_end():
    """All intermediates good, bad is last."""
    async def probe(label):
        return label != "bad"

    b = Bisector(probe)
    intermediates = [f"v{i}" for i in range(4)]
    culprit, probes = await b.find_culprit("good", "bad", intermediates)
    assert culprit == "bad"


@pytest.mark.asyncio
async def test_bisect_probe_exception_treated_as_bad():
    call_count = 0

    async def probe(label):
        nonlocal call_count
        call_count += 1
        if label == "v2":
            raise RuntimeError("probe failed")
        return True  # everything else good

    b = Bisector(probe)
    culprit, probes = await b.find_culprit("good", "bad", ["v0", "v1", "v2", "v3"])
    # v2 raises → treated as bad → culprit is v2 or earlier
    assert culprit in ("v2", "v3", "bad")


@pytest.mark.asyncio
async def test_bisect_log_n_complexity():
    """32 intermediates → ≤ 6 probes."""
    intermediates = [f"v{i}" for i in range(32)]

    async def probe(label):
        if label == "good":
            return True
        if label == "bad":
            return False
        return int(label[1:]) < 20

    b = Bisector(probe)
    culprit, probes = await b.find_culprit("good", "bad", intermediates)
    assert culprit == "v20"
    assert probes <= 6


@pytest.mark.asyncio
async def test_bisect_returns_culprit_not_good():
    """Culprit is the FIRST bad, not the last good."""
    async def probe(label):
        return label in ("good", "v0", "v1")

    b = Bisector(probe)
    culprit, _ = await b.find_culprit("good", "bad", ["v0", "v1", "v2"])
    assert culprit == "v2"
