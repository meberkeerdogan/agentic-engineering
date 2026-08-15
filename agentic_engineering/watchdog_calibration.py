"""Calibrate observe-only watchdog signals from complete human-labelled cases."""

from __future__ import annotations

import argparse
import hashlib
import json
from collections.abc import Mapping, Sequence
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from .watchdog import SIGNAL_TYPES


class CalibrationError(ValueError):
    """Raised when calibration evidence is incomplete or inconsistent."""


@dataclass(frozen=True)
class CalibrationPolicy:
    minimum_labels: int = 5
    minimum_precision: float = 0.8
    minimum_recall: float = 0.8


def _canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"), sort_keys=True)


def _fingerprint(value: Any) -> str:
    return hashlib.sha256(_canonical_json(value).encode("utf-8")).hexdigest()


def _validate_policy(policy: CalibrationPolicy) -> None:
    if (
        isinstance(policy.minimum_labels, bool)
        or not isinstance(policy.minimum_labels, int)
        or policy.minimum_labels < 1
    ):
        raise CalibrationError("minimum_labels must be a positive integer")
    for name, value in (
        ("minimum_precision", policy.minimum_precision),
        ("minimum_recall", policy.minimum_recall),
    ):
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise CalibrationError(f"{name} must be between 0 and 1")
        if not 0 <= value <= 1:
            raise CalibrationError(f"{name} must be between 0 and 1")


def _validate_case(report: Mapping[str, Any], labels: Mapping[str, Any]) -> None:
    if report.get("version") != 1 or labels.get("version") != 1:
        raise CalibrationError("watchdog reports and labels must use version 1")
    report_payload = dict(report)
    stored_fingerprint = report_payload.pop("fingerprint", None)
    stored_report_id = report_payload.pop("report_id", None)
    computed_fingerprint = _fingerprint(report_payload)
    if stored_fingerprint != computed_fingerprint:
        raise CalibrationError("watchdog report fingerprint is invalid")
    if stored_report_id != f"watchdog-report-{computed_fingerprint[:16]}":
        raise CalibrationError("watchdog report ID is invalid")
    if report.get("mode") != "observe_only" or report.get("interventions") != []:
        raise CalibrationError("calibration requires an observe-only watchdog report")
    if labels.get("report_id") != report.get("report_id"):
        raise CalibrationError("label set report ID does not match its watchdog report")
    if labels.get("report_fingerprint") != report.get("fingerprint"):
        raise CalibrationError("label set report fingerprint does not match")

    signals = report.get("signals")
    label_records = labels.get("labels")
    missed = labels.get("missed_signals")
    if not isinstance(signals, list) or not isinstance(label_records, list):
        raise CalibrationError("report signals and labels must be arrays")
    if not isinstance(missed, list):
        raise CalibrationError("missed_signals must be an array")
    signal_ids = [signal.get("id") for signal in signals if isinstance(signal, Mapping)]
    label_ids = [label.get("signal_id") for label in label_records if isinstance(label, Mapping)]
    if len(signal_ids) != len(signals) or len(label_ids) != len(label_records):
        raise CalibrationError("signals and labels must be objects with IDs")
    if len(signal_ids) != len(set(signal_ids)):
        raise CalibrationError("duplicate watchdog signal IDs are not allowed")
    if len(label_ids) != len(set(label_ids)):
        raise CalibrationError("duplicate signal labels are not allowed")
    if set(label_ids) != set(signal_ids):
        missing = sorted(set(signal_ids) - set(label_ids))
        unexpected = sorted(set(label_ids) - set(signal_ids))
        raise CalibrationError(
            f"every signal must be labelled; missing: {missing}; unexpected: {unexpected}"
        )
    for label in label_records:
        if label.get("verdict") not in {"true_positive", "false_positive"}:
            raise CalibrationError("signal verdicts must be true_positive or false_positive")
    missed_keys = []
    for missed_signal in missed:
        if (
            not isinstance(missed_signal, Mapping)
            or missed_signal.get("type") not in SIGNAL_TYPES
        ):
            raise CalibrationError("missed signals require a supported signal type")
        missed_keys.append(
            (
                missed_signal["type"],
                missed_signal.get("start_step"),
                missed_signal.get("end_step"),
            )
        )
    if len(missed_keys) != len(set(missed_keys)):
        raise CalibrationError("duplicate missed-signal windows are not allowed")


def _ratio(numerator: int, denominator: int) -> float | None:
    return round(numerator / denominator, 12) if denominator else None


def calibrate_watchdog(
    calibration_id: str,
    policy: CalibrationPolicy,
    cases: Sequence[tuple[Mapping[str, Any], Mapping[str, Any]]],
) -> dict[str, Any]:
    """Aggregate complete labelled cases into a deterministic calibration report."""

    if not isinstance(calibration_id, str) or not calibration_id:
        raise CalibrationError("calibration requires a non-empty ID")
    _validate_policy(policy)
    if not cases:
        raise CalibrationError("calibration requires at least one labelled case")

    counts = {
        signal_type: {"true_positive": 0, "false_positive": 0, "false_negative": 0}
        for signal_type in SIGNAL_TYPES
    }
    case_fingerprints = []
    seen_reports: set[str] = set()
    for report, labels in cases:
        _validate_case(report, labels)
        report_fingerprint = report["fingerprint"]
        if report_fingerprint in seen_reports:
            raise CalibrationError(
                "duplicate watchdog reports cannot inflate calibration support"
            )
        seen_reports.add(report_fingerprint)
        case_fingerprint = _fingerprint({"report": report, "labels": labels})
        signal_types = {signal["id"]: signal["type"] for signal in report["signals"]}
        for label in labels["labels"]:
            counts[signal_types[label["signal_id"]]][label["verdict"]] += 1
        for missed_signal in labels["missed_signals"]:
            counts[missed_signal["type"]]["false_negative"] += 1
        case_fingerprints.append(case_fingerprint)

    summaries = []
    eligible_types = []
    for signal_type in sorted(SIGNAL_TYPES):
        type_counts = counts[signal_type]
        detected = type_counts["true_positive"] + type_counts["false_positive"]
        actual = type_counts["true_positive"] + type_counts["false_negative"]
        support = detected + type_counts["false_negative"]
        precision = _ratio(type_counts["true_positive"], detected)
        recall = _ratio(type_counts["true_positive"], actual)
        eligible = bool(
            support >= policy.minimum_labels
            and precision is not None
            and recall is not None
            and precision >= policy.minimum_precision
            and recall >= policy.minimum_recall
        )
        summary = {
            "signal_type": signal_type,
            **type_counts,
            "support": support,
            "precision": precision,
            "recall": recall,
            "false_positive_rate": _ratio(type_counts["false_positive"], detected),
            "eligible_for_advisory_experiment": eligible,
        }
        summaries.append(summary)
        if eligible:
            eligible_types.append(signal_type)

    totals = {
        key: sum(item[key] for item in counts.values())
        for key in ("true_positive", "false_positive", "false_negative")
    }
    detected_total = totals["true_positive"] + totals["false_positive"]
    actual_total = totals["true_positive"] + totals["false_negative"]
    report: dict[str, Any] = {
        "version": 1,
        "calibration_id": calibration_id,
        "mode": "calibration_only",
        "policy": asdict(policy),
        "case_count": len(cases),
        "case_fingerprints": sorted(case_fingerprints),
        "type_summaries": summaries,
        "overall": {
            **totals,
            "precision": _ratio(totals["true_positive"], detected_total),
            "recall": _ratio(totals["true_positive"], actual_total),
            "false_positive_rate": _ratio(totals["false_positive"], detected_total),
        },
        "eligible_advisory_types": eligible_types,
        "interventions": [],
    }
    fingerprint = _fingerprint(report)
    report["report_id"] = f"watchdog-calibration-{fingerprint[:16]}"
    report["fingerprint"] = fingerprint
    return report


def _resolve_inside(root: Path, relative: str) -> Path:
    root = root.resolve()
    candidate = (root / relative).resolve()
    try:
        candidate.relative_to(root)
    except ValueError as error:
        raise CalibrationError(f"calibration path escapes manifest root: {relative}") from error
    return candidate


def load_manifest(path: Path) -> tuple[str, CalibrationPolicy, list[tuple[dict, dict]]]:
    manifest = json.loads(path.read_text(encoding="utf-8"))
    try:
        policy = CalibrationPolicy(**manifest["policy"])
        cases = []
        for case in manifest["cases"]:
            report_path = _resolve_inside(path.parent, case["report"])
            labels_path = _resolve_inside(path.parent, case["labels"])
            cases.append(
                (
                    json.loads(report_path.read_text(encoding="utf-8")),
                    json.loads(labels_path.read_text(encoding="utf-8")),
                )
            )
        return manifest["calibration_id"], policy, cases
    except (KeyError, TypeError) as error:
        raise CalibrationError("invalid calibration manifest") from error


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    arguments = parser.parse_args(argv)
    calibration_id, policy, cases = load_manifest(arguments.manifest)
    report = calibrate_watchdog(calibration_id, policy, cases)
    arguments.output.parent.mkdir(parents=True, exist_ok=True)
    arguments.output.write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
