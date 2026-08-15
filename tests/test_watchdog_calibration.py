import json
from copy import deepcopy
from pathlib import Path

import pytest
from test_core_schemas import load_json

from agentic_engineering.watchdog_calibration import (
    CalibrationError,
    CalibrationPolicy,
    calibrate_watchdog,
    load_manifest,
    main,
)

ROOT = Path(__file__).resolve().parents[1]


def case() -> tuple[dict, dict]:
    return (
        load_json("examples/expected-watchdog-report.json"),
        load_json("examples/watchdog-labels.json"),
    )


def policy() -> CalibrationPolicy:
    return CalibrationPolicy(minimum_labels=1)


def test_fixture_produces_exact_golden_calibration() -> None:
    report = calibrate_watchdog("calibration-watchdog-fixture", policy(), [case()])

    assert report == load_json("examples/expected-watchdog-calibration.json")


def test_repeated_calibration_is_byte_stable_and_does_not_mutate_inputs() -> None:
    source_case = case()
    original = deepcopy(source_case)

    first = calibrate_watchdog("calibration-watchdog-fixture", policy(), [source_case])
    second = calibrate_watchdog("calibration-watchdog-fixture", policy(), [source_case])

    assert source_case == original
    assert json.dumps(first, sort_keys=True) == json.dumps(second, sort_keys=True)


def test_every_detected_signal_requires_exactly_one_label() -> None:
    report, labels = case()
    labels["labels"].pop()

    with pytest.raises(CalibrationError, match="every signal must be labelled"):
        calibrate_watchdog("incomplete", policy(), [(report, labels)])


def test_labels_are_bound_to_the_exact_watchdog_report() -> None:
    report, labels = case()
    labels["report_fingerprint"] = "0" * 64

    with pytest.raises(CalibrationError, match="fingerprint does not match"):
        calibrate_watchdog("mismatch", policy(), [(report, labels)])


def test_tampered_watchdog_report_is_rejected() -> None:
    report, labels = case()
    report["signals"][0]["summary"] = "tampered after watchdog analysis"

    with pytest.raises(CalibrationError, match="report fingerprint is invalid"):
        calibrate_watchdog("tampered", policy(), [(report, labels)])


def test_duplicate_labelled_cases_cannot_inflate_support() -> None:
    source_case = case()

    with pytest.raises(CalibrationError, match="duplicate watchdog reports"):
        calibrate_watchdog("duplicate", policy(), [source_case, source_case])


def test_missed_signal_is_counted_as_false_negative() -> None:
    report, labels = case()
    labels["missed_signals"].append(
        {
            "type": "stagnation",
            "start_step": 1,
            "end_step": 2,
            "rationale": "Reviewer found an additional stagnant window.",
            "evidence_refs": ["review/missed-1.json"],
        }
    )

    calibration = calibrate_watchdog("with-miss", policy(), [(report, labels)])
    stagnation = next(
        item
        for item in calibration["type_summaries"]
        if item["signal_type"] == "stagnation"
    )

    assert stagnation["false_negative"] == 1
    assert stagnation["recall"] == 0.5
    assert stagnation["eligible_for_advisory_experiment"] is False


def test_default_support_threshold_prevents_fixture_overclaim() -> None:
    calibration = calibrate_watchdog(
        "default-threshold", CalibrationPolicy(), [case()]
    )

    assert calibration["eligible_advisory_types"] == []
    assert calibration["interventions"] == []


def test_manifest_paths_cannot_escape_the_manifest_directory(tmp_path: Path) -> None:
    manifest = tmp_path / "manifest.json"
    manifest.write_text(
        json.dumps(
            {
                "version": 1,
                "calibration_id": "escape",
                "policy": {
                    "minimum_labels": 1,
                    "minimum_precision": 0.8,
                    "minimum_recall": 0.8,
                },
                "cases": [{"report": "../report.json", "labels": "labels.json"}],
            }
        ),
        encoding="utf-8",
    )

    with pytest.raises(CalibrationError, match="escapes manifest root"):
        load_manifest(manifest)


def test_cli_writes_golden_calibration(tmp_path: Path) -> None:
    output = tmp_path / "calibration.json"

    exit_code = main(
        [
            str(ROOT / "examples" / "watchdog-calibration.json"),
            "--output",
            str(output),
        ]
    )

    assert exit_code == 0
    assert json.loads(output.read_text(encoding="utf-8")) == load_json(
        "examples/expected-watchdog-calibration.json"
    )
