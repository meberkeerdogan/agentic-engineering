"""Build deterministic, calibration-gated watchdog advice without interventions."""

from __future__ import annotations

import argparse
import hashlib
import json
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

from .watchdog import SIGNAL_TYPES


class AdvisoryError(ValueError):
    """Raised when advisory inputs are invalid or not calibration-bound."""


MESSAGES = {
    "repeated_action": "Review whether this repeated action produced new evidence.",
    "stagnation": "Review the unchanged-state window before continuing.",
    "action_oscillation": "Review the alternating actions and choose one evidenced direction.",
    "premature_patching": "Review whether reproduction evidence is required before further patching.",
    "skipped_validation": "Run or cite the required validation before claiming completion.",
}


def _canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"), sort_keys=True)


def _fingerprint(value: Any) -> str:
    return hashlib.sha256(_canonical_json(value).encode("utf-8")).hexdigest()


def _validate_fingerprint(report: Mapping[str, Any], prefix: str) -> None:
    payload = dict(report)
    stored_fingerprint = payload.pop("fingerprint", None)
    stored_id = payload.pop("report_id", None)
    computed = _fingerprint(payload)
    if stored_fingerprint != computed or stored_id != f"{prefix}-{computed[:16]}":
        raise AdvisoryError(f"{prefix} fingerprint is invalid")


def _eligible_types(calibration: Mapping[str, Any]) -> set[str]:
    _validate_fingerprint(calibration, "watchdog-calibration")
    if calibration.get("mode") != "calibration_only" or calibration.get("interventions") != []:
        raise AdvisoryError("advice requires a calibration-only report")
    summaries = calibration.get("type_summaries")
    policy = calibration.get("policy")
    declared = calibration.get("eligible_advisory_types")
    if not isinstance(summaries, list) or not isinstance(policy, Mapping):
        raise AdvisoryError("calibration summaries and policy are required")
    if not isinstance(declared, list) or len(declared) != len(set(declared)):
        raise AdvisoryError("eligible advisory types must be unique")
    derived: set[str] = set()
    observed: set[str] = set()
    for summary in summaries:
        if not isinstance(summary, Mapping) or summary.get("signal_type") not in SIGNAL_TYPES:
            raise AdvisoryError("calibration contains an unsupported signal type")
        signal_type = summary["signal_type"]
        if signal_type in observed:
            raise AdvisoryError("calibration signal summaries must be unique")
        observed.add(signal_type)
        if summary.get("eligible_for_advisory_experiment"):
            if (
                summary.get("support", 0) < policy.get("minimum_labels", 1)
                or summary.get("precision") is None
                or summary.get("recall") is None
                or summary["precision"] < policy.get("minimum_precision", 1)
                or summary["recall"] < policy.get("minimum_recall", 1)
            ):
                raise AdvisoryError("calibration eligibility violates its policy")
            derived.add(signal_type)
    if observed != SIGNAL_TYPES or set(declared) != derived:
        raise AdvisoryError("declared advisory eligibility is inconsistent")
    return derived


def build_advisory_report(
    watchdog_report: Mapping[str, Any], calibration: Mapping[str, Any]
) -> dict[str, Any]:
    """Return advice only for signal types promoted by exact calibration evidence."""

    _validate_fingerprint(watchdog_report, "watchdog-report")
    if watchdog_report.get("mode") != "observe_only" or watchdog_report.get("interventions") != []:
        raise AdvisoryError("advice requires an observe-only watchdog report")
    signals = watchdog_report.get("signals")
    if not isinstance(signals, list) or watchdog_report.get("signal_count") != len(signals):
        raise AdvisoryError("watchdog signal count is inconsistent")
    eligible = _eligible_types(calibration)
    advice = []
    seen_ids: set[str] = set()
    for signal in signals:
        if not isinstance(signal, Mapping) or signal.get("type") not in SIGNAL_TYPES:
            raise AdvisoryError("watchdog contains an unsupported signal")
        signal_id = signal.get("id")
        if not isinstance(signal_id, str) or signal_id in seen_ids:
            raise AdvisoryError("watchdog signal IDs must be unique strings")
        seen_ids.add(signal_id)
        if signal["type"] not in eligible:
            continue
        advice.append(
            {
                "id": f"advice-{len(advice) + 1:03d}-{signal['type']}",
                "signal_id": signal_id,
                "signal_type": signal["type"],
                "message": MESSAGES[signal["type"]],
                "delivery": "next_safe_boundary",
                "evidence_refs": list(signal.get("evidence_refs", [])),
            }
        )
    report: dict[str, Any] = {
        "version": 1,
        "mode": "advisory_experiment_only",
        "watchdog_report_id": watchdog_report["report_id"],
        "watchdog_fingerprint": watchdog_report["fingerprint"],
        "calibration_report_id": calibration["report_id"],
        "calibration_fingerprint": calibration["fingerprint"],
        "eligible_signal_types": sorted(eligible),
        "advice": advice,
        "interventions": [],
        "blocking_actions": [],
    }
    fingerprint = _fingerprint(report)
    report["report_id"] = f"advisory-report-{fingerprint[:16]}"
    report["fingerprint"] = fingerprint
    return report


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("watchdog_report", type=Path)
    parser.add_argument("calibration_report", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    arguments = parser.parse_args(argv)
    watchdog_report = json.loads(arguments.watchdog_report.read_text("utf-8"))
    calibration = json.loads(arguments.calibration_report.read_text("utf-8"))
    report = build_advisory_report(watchdog_report, calibration)
    arguments.output.parent.mkdir(parents=True, exist_ok=True)
    arguments.output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
