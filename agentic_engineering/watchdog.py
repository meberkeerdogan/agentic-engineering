"""Observe-only trajectory monitoring for coding-agent calibration."""

from __future__ import annotations

import argparse
import hashlib
import json
from collections.abc import Mapping, Sequence
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any


class WatchdogError(ValueError):
    """Raised when a trajectory or watchdog configuration is invalid."""


SUPPORTED_PHASES = {"navigate", "reproduce", "patch", "validate", "complete"}


@dataclass(frozen=True)
class WatchdogConfig:
    repeat_threshold: int = 3
    stagnation_threshold: int = 4
    oscillation_cycles: int = 2


def _canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"), sort_keys=True)


def _validate_config(config: WatchdogConfig) -> None:
    for name, value, minimum in (
        ("repeat_threshold", config.repeat_threshold, 2),
        ("stagnation_threshold", config.stagnation_threshold, 2),
        ("oscillation_cycles", config.oscillation_cycles, 2),
    ):
        if isinstance(value, bool) or not isinstance(value, int) or value < minimum:
            raise WatchdogError(f"{name} must be an integer of at least {minimum}")


def _validate_trajectory(trajectory: Mapping[str, Any]) -> list[Mapping[str, Any]]:
    if trajectory.get("version") != 1:
        raise WatchdogError("trajectory version must be 1")
    if not isinstance(trajectory.get("trajectory_id"), str) or not trajectory[
        "trajectory_id"
    ]:
        raise WatchdogError("trajectory requires a non-empty ID")
    if not isinstance(trajectory.get("task_id"), str) or not trajectory["task_id"]:
        raise WatchdogError("trajectory requires a non-empty task ID")
    events = trajectory.get("events")
    if not isinstance(events, list) or not events:
        raise WatchdogError("trajectory requires at least one event")

    previous_step = 0
    required_strings = ("phase", "action", "target", "state_fingerprint")
    for event in events:
        if not isinstance(event, Mapping):
            raise WatchdogError("trajectory events must be objects")
        step = event.get("step")
        if isinstance(step, bool) or not isinstance(step, int) or step <= previous_step:
            raise WatchdogError("event steps must be strictly increasing positive integers")
        previous_step = step
        if any(
            not isinstance(event.get(field), str) or not event[field]
            for field in required_strings
        ):
            raise WatchdogError("event phase, action, target, and state must be strings")
        if event["phase"] not in SUPPORTED_PHASES:
            raise WatchdogError(f"unsupported event phase: {event['phase']}")
        evidence_refs = event.get("evidence_refs")
        if (
            not isinstance(evidence_refs, list)
            or not evidence_refs
            or any(not isinstance(ref, str) or not ref for ref in evidence_refs)
            or len(evidence_refs) != len(set(evidence_refs))
        ):
            raise WatchdogError("every event requires unique evidence references")
    return events


def _evidence(events: Sequence[Mapping[str, Any]]) -> list[str]:
    return sorted({ref for event in events for ref in event["evidence_refs"]})


def _signal(
    signal_type: str,
    category: str,
    events: Sequence[Mapping[str, Any]],
    summary: str,
) -> dict[str, Any]:
    return {
        "type": signal_type,
        "category": category,
        "start_step": events[0]["step"],
        "end_step": events[-1]["step"],
        "summary": summary,
        "evidence_refs": _evidence(events),
    }


def _repeated_actions(
    events: Sequence[Mapping[str, Any]], threshold: int
) -> list[dict[str, Any]]:
    signals = []
    streak_start = 0
    for index, event in enumerate(events):
        signature = (event["action"], event["target"])
        previous = (
            (events[index - 1]["action"], events[index - 1]["target"])
            if index
            else None
        )
        if signature != previous:
            streak_start = index
        streak_length = index - streak_start + 1
        if streak_length == threshold:
            window = events[streak_start : index + 1]
            signals.append(
                _signal(
                    "repeated_action",
                    "advisory_candidate",
                    window,
                    f"action {event['action']} repeated on {event['target']}",
                )
            )
    return signals


def _stagnation(
    events: Sequence[Mapping[str, Any]], threshold: int
) -> list[dict[str, Any]]:
    signals = []
    streak_start = 0
    for index, event in enumerate(events):
        previous = events[index - 1]["state_fingerprint"] if index else None
        if event["state_fingerprint"] != previous:
            streak_start = index
        streak_length = index - streak_start + 1
        if streak_length == threshold:
            window = events[streak_start : index + 1]
            signals.append(
                _signal(
                    "stagnation",
                    "advisory_candidate",
                    window,
                    f"external state did not change for {threshold} events",
                )
            )
    return signals


def _oscillation(
    events: Sequence[Mapping[str, Any]], cycles: int
) -> list[dict[str, Any]]:
    signals = []
    window_size = cycles * 2
    active = False
    for index in range(2, len(events)):
        current = (events[index]["action"], events[index]["target"])
        two_back = (events[index - 2]["action"], events[index - 2]["target"])
        if current != two_back:
            active = False
            continue
        if index + 1 < window_size or active:
            continue
        window = events[index + 1 - window_size : index + 1]
        signatures = [(event["action"], event["target"]) for event in window]
        if signatures[0] != signatures[1] and all(
            signature == signatures[position % 2]
            for position, signature in enumerate(signatures)
        ):
            signals.append(
                _signal(
                    "action_oscillation",
                    "blocking_candidate",
                    window,
                    "actions alternated without escaping the two-action cycle",
                )
            )
            active = True
    return signals


def _phase_order_signals(events: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    signals = []
    reproduced = False
    last_patch_index: int | None = None
    last_validation_index: int | None = None
    premature_reported = False

    for index, event in enumerate(events):
        phase = event["phase"]
        if phase == "reproduce":
            reproduced = True
        elif phase == "patch":
            last_patch_index = index
            if not reproduced and not premature_reported:
                signals.append(
                    _signal(
                        "premature_patching",
                        "blocking_candidate",
                        [event],
                        "patching began before a reproduction event",
                    )
                )
                premature_reported = True
        elif phase == "validate":
            last_validation_index = index
        elif (
            phase == "complete"
            and last_patch_index is not None
            and (last_validation_index is None or last_validation_index < last_patch_index)
        ):
            signals.append(
                _signal(
                    "skipped_validation",
                    "blocking_candidate",
                    events[last_patch_index : index + 1],
                    "completion was claimed after a patch without later validation",
                )
            )
    return signals


def analyze_trajectory(
    trajectory: Mapping[str, Any], config: WatchdogConfig | None = None
) -> dict[str, Any]:
    """Detect candidate failure signals without changing the trajectory."""

    selected_config = config or WatchdogConfig()
    _validate_config(selected_config)
    events = _validate_trajectory(trajectory)
    signals = [
        *_repeated_actions(events, selected_config.repeat_threshold),
        *_stagnation(events, selected_config.stagnation_threshold),
        *_oscillation(events, selected_config.oscillation_cycles),
        *_phase_order_signals(events),
    ]
    signals.sort(key=lambda signal: (signal["end_step"], signal["type"]))
    for index, signal in enumerate(signals, start=1):
        signal["id"] = f"signal-{index:03d}-{signal['type']}"

    report: dict[str, Any] = {
        "version": 1,
        "trajectory_id": trajectory["trajectory_id"],
        "task_id": trajectory["task_id"],
        "trajectory_fingerprint": hashlib.sha256(
            _canonical_json(trajectory).encode("utf-8")
        ).hexdigest(),
        "mode": "observe_only",
        "config": asdict(selected_config),
        "event_count": len(events),
        "signal_count": len(signals),
        "signals": signals,
        "interventions": [],
    }
    fingerprint = hashlib.sha256(_canonical_json(report).encode("utf-8")).hexdigest()
    report["report_id"] = f"watchdog-report-{fingerprint[:16]}"
    report["fingerprint"] = fingerprint
    return report


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("trajectory", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--repeat-threshold", type=int, default=3)
    parser.add_argument("--stagnation-threshold", type=int, default=4)
    parser.add_argument("--oscillation-cycles", type=int, default=2)
    arguments = parser.parse_args(argv)
    trajectory = json.loads(arguments.trajectory.read_text(encoding="utf-8"))
    config = WatchdogConfig(
        repeat_threshold=arguments.repeat_threshold,
        stagnation_threshold=arguments.stagnation_threshold,
        oscillation_cycles=arguments.oscillation_cycles,
    )
    report = analyze_trajectory(trajectory, config)
    arguments.output.parent.mkdir(parents=True, exist_ok=True)
    arguments.output.write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
