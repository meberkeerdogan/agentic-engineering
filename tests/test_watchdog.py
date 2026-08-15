import json
from copy import deepcopy
from pathlib import Path

import pytest
from test_core_schemas import load_json

from agentic_engineering.watchdog import (
    WatchdogConfig,
    WatchdogError,
    analyze_trajectory,
    main,
)

ROOT = Path(__file__).resolve().parents[1]


def trajectory() -> dict:
    return load_json("examples/watchdog-trajectory.json")


def test_fixture_produces_exact_golden_report() -> None:
    assert analyze_trajectory(trajectory()) == load_json(
        "examples/expected-watchdog-report.json"
    )


def test_repeated_analysis_is_byte_stable_and_does_not_mutate_input() -> None:
    source = trajectory()
    original = deepcopy(source)

    first = analyze_trajectory(source)
    second = analyze_trajectory(source)

    assert source == original
    assert json.dumps(first, sort_keys=True) == json.dumps(second, sort_keys=True)


def test_healthy_reproduce_patch_validate_flow_has_no_signals() -> None:
    source = trajectory()
    source["events"] = [
        {"step": 1, "phase": "navigate", "action": "open", "target": "issue", "state_fingerprint": "s0", "evidence_refs": ["e/1"]},
        {"step": 2, "phase": "reproduce", "action": "run", "target": "test", "state_fingerprint": "s1", "evidence_refs": ["e/2"]},
        {"step": 3, "phase": "patch", "action": "edit", "target": "app.py", "state_fingerprint": "s2", "evidence_refs": ["e/3"]},
        {"step": 4, "phase": "validate", "action": "run", "target": "suite", "state_fingerprint": "s3", "evidence_refs": ["e/4"]},
        {"step": 5, "phase": "complete", "action": "claim", "target": "task", "state_fingerprint": "s4", "evidence_refs": ["e/5"]}
    ]

    report = analyze_trajectory(source)

    assert report["signal_count"] == 0
    assert report["signals"] == []
    assert report["interventions"] == []


def test_custom_thresholds_are_recorded_and_applied() -> None:
    config = WatchdogConfig(
        repeat_threshold=4, stagnation_threshold=5, oscillation_cycles=3
    )

    report = analyze_trajectory(trajectory(), config)
    signal_types = {signal["type"] for signal in report["signals"]}

    assert report["config"] == {
        "repeat_threshold": 4,
        "stagnation_threshold": 5,
        "oscillation_cycles": 3,
    }
    assert "repeated_action" not in signal_types
    assert "action_oscillation" not in signal_types


def test_event_steps_must_be_strictly_increasing() -> None:
    source = trajectory()
    source["events"][1]["step"] = 1

    with pytest.raises(WatchdogError, match="strictly increasing"):
        analyze_trajectory(source)


def test_unknown_event_phase_is_rejected() -> None:
    source = trajectory()
    source["events"][0]["phase"] = "think"

    with pytest.raises(WatchdogError, match="unsupported event phase"):
        analyze_trajectory(source)


def test_thresholds_reject_boolean_and_small_values() -> None:
    with pytest.raises(WatchdogError, match="repeat_threshold"):
        analyze_trajectory(trajectory(), WatchdogConfig(repeat_threshold=True))

    with pytest.raises(WatchdogError, match="oscillation_cycles"):
        analyze_trajectory(trajectory(), WatchdogConfig(oscillation_cycles=1))


def test_cli_writes_golden_report(tmp_path: Path) -> None:
    output = tmp_path / "watchdog-report.json"

    exit_code = main(
        [
            str(ROOT / "examples" / "watchdog-trajectory.json"),
            "--output",
            str(output),
        ]
    )

    assert exit_code == 0
    assert json.loads(output.read_text(encoding="utf-8")) == load_json(
        "examples/expected-watchdog-report.json"
    )
