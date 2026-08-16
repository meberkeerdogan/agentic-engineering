import copy
import json
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator

from agentic_engineering.advisory_watchdog import AdvisoryError, build_advisory_report


ROOT = Path(__file__).resolve().parents[1]


def load_example(name: str) -> dict:
    return json.loads((ROOT / "examples" / name).read_text("utf-8"))


def test_fixture_calibration_emits_only_eligible_advice() -> None:
    report = build_advisory_report(
        load_example("expected-watchdog-report.json"),
        load_example("expected-watchdog-calibration.json"),
    )

    assert report == load_example("expected-advisory-report.json")
    assert {item["signal_type"] for item in report["advice"]} == {
        "repeated_action",
        "stagnation",
        "premature_patching",
        "skipped_validation",
    }
    assert report["interventions"] == []
    assert report["blocking_actions"] == []
    schema = json.loads((ROOT / "schemas" / "advisory-report.schema.json").read_text("utf-8"))
    assert not list(Draft202012Validator(schema).iter_errors(report))


def test_real_calibration_emits_no_advice() -> None:
    watchdog = json.loads(
        (
            ROOT
            / "research/calibration/representative-sentinel-001/control-watchdog-report.json"
        ).read_text("utf-8")
    )
    calibration = json.loads(
        (ROOT / "research/calibration/expected-live-sentinels-calibration.json").read_text(
            "utf-8"
        )
    )

    report = build_advisory_report(watchdog, calibration)

    assert report["eligible_signal_types"] == []
    assert report["advice"] == []
    assert report["interventions"] == []


@pytest.mark.parametrize("target", ["watchdog", "calibration"])
def test_tampered_inputs_fail_closed(target: str) -> None:
    watchdog = load_example("expected-watchdog-report.json")
    calibration = load_example("expected-watchdog-calibration.json")
    selected = watchdog if target == "watchdog" else calibration
    selected["fingerprint"] = "0" * 64

    with pytest.raises(AdvisoryError, match="fingerprint"):
        build_advisory_report(watchdog, calibration)


def test_inconsistent_eligibility_fails_even_with_refingerprinting() -> None:
    calibration = copy.deepcopy(load_example("expected-watchdog-calibration.json"))
    calibration["eligible_advisory_types"].append("action_oscillation")
    payload = dict(calibration)
    payload.pop("report_id")
    payload.pop("fingerprint")
    from agentic_engineering.advisory_watchdog import _fingerprint

    fingerprint = _fingerprint(payload)
    calibration["fingerprint"] = fingerprint
    calibration["report_id"] = f"watchdog-calibration-{fingerprint[:16]}"

    with pytest.raises(AdvisoryError, match="inconsistent"):
        build_advisory_report(load_example("expected-watchdog-report.json"), calibration)
