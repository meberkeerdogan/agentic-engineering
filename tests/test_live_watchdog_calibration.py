import json
from pathlib import Path

from jsonschema import Draft202012Validator

from agentic_engineering.watchdog_calibration import calibrate_watchdog, load_manifest


ROOT = Path(__file__).resolve().parents[1]
DATASET = ROOT / "research" / "calibration" / "representative-sentinel-001"


def test_real_sentinel_cases_are_complete_private_and_ineligible() -> None:
    calibration_id, policy, cases = load_manifest(DATASET / "calibration.json")
    report = calibrate_watchdog(calibration_id, policy, cases)
    expected = json.loads(
        (DATASET / "expected-calibration-report.json").read_text("utf-8")
    )

    assert report == expected
    assert report["case_count"] == 2
    assert report["mode"] == "calibration_only"
    assert report["interventions"] == []
    assert report["eligible_advisory_types"] == []
    assert report["overall"] == {
        "true_positive": 0,
        "false_positive": 2,
        "false_negative": 0,
        "precision": 0.0,
        "recall": None,
        "false_positive_rate": 1.0,
    }
    premature = next(
        item
        for item in report["type_summaries"]
        if item["signal_type"] == "premature_patching"
    )
    assert premature["support"] == 2
    assert premature["eligible_for_advisory_experiment"] is False

    serialized_cases = json.dumps(cases)
    for private_fragment in (
        "aggregated_output",
        "agent_message",
        "python -m unittest",
        "stdout.txt",
    ):
        assert private_fragment not in serialized_cases


def test_real_sentinel_calibration_files_match_public_schemas() -> None:
    pairs = [
        ("watchdog-calibration.schema.json", "calibration.json"),
        ("watchdog-report.schema.json", "control-watchdog-report.json"),
        ("watchdog-report.schema.json", "treatment-watchdog-report.json"),
        ("watchdog-labels.schema.json", "control-labels.json"),
        ("watchdog-labels.schema.json", "treatment-labels.json"),
        (
            "watchdog-calibration-report.schema.json",
            "expected-calibration-report.json",
        ),
    ]
    for schema_name, evidence_name in pairs:
        schema = json.loads((ROOT / "schemas" / schema_name).read_text("utf-8"))
        evidence = json.loads((DATASET / evidence_name).read_text("utf-8"))
        assert not list(Draft202012Validator(schema).iter_errors(evidence))
