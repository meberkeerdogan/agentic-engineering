import copy
import json
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator

from agentic_engineering.paper_reproduction import ReproductionError, run_reproduction


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "research/reproductions/progress-mirage-claim/reproduction.json"


def manifest() -> dict:
    return json.loads(MANIFEST.read_text("utf-8"))


def test_progress_mirage_claim_reproduction_is_traceable_and_deterministic() -> None:
    first = run_reproduction(ROOT, manifest())
    second = run_reproduction(ROOT, manifest())
    expected = json.loads(
        (ROOT / "research/reproductions/progress-mirage-claim/expected-report.json").read_text("utf-8")
    )
    assert first == second == expected
    assert first["scope"] == "claim_level"
    assert first["outcome"] == "supported_in_fixture"
    assert all(item["passed"] for item in first["criterion_results"])
    assert len(first["deviations"]) == 2
    assert first["model_calls_performed"] is False
    manifest_schema = json.loads(
        (ROOT / "schemas/paper-reproduction.schema.json").read_text("utf-8")
    )
    report_schema = json.loads(
        (ROOT / "schemas/paper-reproduction-report.schema.json").read_text("utf-8")
    )
    assert not list(Draft202012Validator(manifest_schema).iter_errors(manifest()))
    assert not list(Draft202012Validator(report_schema).iter_errors(first))


def test_tampered_paper_or_lineage_fails_closed() -> None:
    value = manifest()
    value["paper"]["sha256"] = "0" * 64
    with pytest.raises(ReproductionError, match="paper artifact hash"):
        run_reproduction(ROOT, value)
    value = manifest()
    value["lineage"][0]["sha256"] = "0" * 64
    with pytest.raises(ReproductionError, match="lineage hash"):
        run_reproduction(ROOT, value)


def test_changed_observation_and_path_escape_fail_closed() -> None:
    value = copy.deepcopy(manifest())
    value["experiments"][0]["expected_observation"]["divergence"] = False
    with pytest.raises(ReproductionError, match="observation changed"):
        run_reproduction(ROOT, value)
    value = manifest()
    value["paper"]["pdf_ref"] = "../outside.pdf"
    with pytest.raises(ReproductionError, match="escapes"):
        run_reproduction(ROOT, value)
