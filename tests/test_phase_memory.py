import json
from pathlib import Path

import pytest

from agentic_engineering.phase_memory import PhaseMemoryError, build_memory_view


ROOT = Path(__file__).resolve().parents[1]


def manifest() -> dict:
    return json.loads((ROOT / "examples/phase-memory.json").read_text("utf-8"))


def test_memory_is_bounded_phase_aware_and_deterministic() -> None:
    first = build_memory_view(manifest())
    second = build_memory_view(manifest())
    expected = json.loads((ROOT / "examples/expected-phase-memory.json").read_text("utf-8"))
    assert first == second == expected
    assert first["superseded_entry_ids"] == ["nav-old"]
    assert first["evicted_entry_ids"] == ["patch-old"]
    assert [entry["id"] for entry in first["retrieved_entries"]] == [
        "patch-latest",
        "patch-main",
        "repro-main",
    ]
    assert first["writes"] == []
    assert first["state_mutations"] == []


def test_invalid_supersession_fails_closed() -> None:
    value = manifest()
    value["entries"][1]["supersedes"] = "missing"
    with pytest.raises(PhaseMemoryError, match="declared"):
        build_memory_view(value)


def test_invalid_capacity_and_query_fail_closed() -> None:
    value = manifest()
    value["capacity_per_phase"] = 0
    with pytest.raises(PhaseMemoryError, match="positive"):
        build_memory_view(value)
    value = manifest()
    value["query"]["phase"] = "unknown"
    with pytest.raises(PhaseMemoryError, match="query phase"):
        build_memory_view(value)
