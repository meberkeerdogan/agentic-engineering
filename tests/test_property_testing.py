import json
from pathlib import Path

import pytest

from agentic_engineering.property_testing import PropertyTestingError, evaluate_property_evidence


ROOT = Path(__file__).resolve().parents[1]


def manifest() -> dict:
    return json.loads((ROOT / "examples/property-testing.json").read_text("utf-8"))


def test_reviewed_property_evidence_is_deterministic_and_complementary() -> None:
    first = evaluate_property_evidence(manifest())
    second = evaluate_property_evidence(manifest())
    expected = json.loads((ROOT / "examples/expected-property-testing.json").read_text("utf-8"))
    assert first == second == expected
    assert first["accepted_proposal_ids"] == ["no-mutation", "normalized-sort"]
    assert first["rejected_proposal_ids"] == ["invented-limit"]
    assert first["counterexample_proposal_ids"] == ["no-mutation"]
    assert first["executions"] == []
    assert first["state_mutations"] == []


def test_rejected_property_cannot_supply_result() -> None:
    value = manifest()
    value["results"].append({"proposal_id": "invented-limit", "outcome": "pass", "read_only": True, "evidence_refs": ["bad.json"]})
    with pytest.raises(PropertyTestingError, match="accepted"):
        evaluate_property_evidence(value)


def test_every_proposal_requires_independent_review_and_result() -> None:
    value = manifest()
    value["reviews"].pop()
    with pytest.raises(PropertyTestingError, match="every proposal"):
        evaluate_property_evidence(value)
    value = manifest()
    value["results"].pop()
    with pytest.raises(PropertyTestingError, match="missing results"):
        evaluate_property_evidence(value)
