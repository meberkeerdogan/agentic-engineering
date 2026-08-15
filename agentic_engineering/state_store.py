"""Append-only, evidence-derived state for verified engineering runs."""

from __future__ import annotations

import hashlib
import json
import os
import re
from collections.abc import Mapping
from copy import deepcopy
from pathlib import Path
from typing import Any


class StateTransitionError(ValueError):
    """Raised when an event would violate verified-state invariants."""


GENESIS_HASH = "0" * 64
ID_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")


def _canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"), sort_keys=True)


def _event_hash(event_without_hash: Mapping[str, Any]) -> str:
    return hashlib.sha256(_canonical_json(event_without_hash).encode("utf-8")).hexdigest()


def _require_id(value: Any, label: str) -> str:
    if not isinstance(value, str) or not ID_PATTERN.fullmatch(value):
        raise StateTransitionError(f"{label} is not a valid ID: {value!r}")
    return value


def _parse_timestamp(value: str):
    from datetime import datetime

    try:
        parsed = datetime.fromisoformat(value)
    except (TypeError, ValueError) as error:
        raise StateTransitionError(f"invalid event timestamp: {value!r}") from error
    if parsed.tzinfo is None:
        raise StateTransitionError("event timestamp must include a timezone")
    return parsed


def _validate_evaluation_report(report: Mapping[str, Any]) -> None:
    required_fields = {
        "version",
        "contract_id",
        "work_item_id",
        "spec_id",
        "outcome",
        "criterion_results",
        "evaluator_results",
        "regressions",
        "report_id",
        "fingerprint",
    }
    if set(report) != required_fields:
        raise StateTransitionError("evaluation report fields do not match the contract")
    if report.get("version") != 1 or report.get("outcome") not in {
        "pass",
        "fail",
        "error",
    }:
        raise StateTransitionError("evaluation report has invalid version or outcome")
    for field in ("contract_id", "work_item_id", "spec_id", "report_id"):
        _require_id(report.get(field), f"evaluation report {field}")
    if not isinstance(report.get("evaluator_results"), list) or not report[
        "evaluator_results"
    ]:
        raise StateTransitionError("evaluation report contains no evaluator evidence")
    if not all(isinstance(result, Mapping) for result in report["evaluator_results"]):
        raise StateTransitionError("evaluation result must be an object")
    result_ids = [
        _require_id(result.get("evaluator_id"), "evaluator result ID")
        for result in report["evaluator_results"]
    ]
    if len(result_ids) != len(set(result_ids)):
        raise StateTransitionError("evaluation report evaluator IDs are invalid")
    if any(
        result.get("outcome") not in {"pass", "fail", "error"}
        for result in report["evaluator_results"]
    ):
        raise StateTransitionError("evaluation report contains an invalid result outcome")
    for result in report["evaluator_results"]:
        if result.get("type") not in {"command", "artifact", "rubric", "world_state"}:
            raise StateTransitionError("evaluation report contains an invalid evaluator type")
        artifact_refs = result.get("artifact_refs")
        if not isinstance(artifact_refs, list) or not all(
            isinstance(reference, str) and reference for reference in artifact_refs
        ):
            raise StateTransitionError("evaluation report artifact references are invalid")
    if not isinstance(report.get("criterion_results"), list) or not all(
        isinstance(criterion, Mapping) for criterion in report["criterion_results"]
    ):
        raise StateTransitionError("evaluation report criteria are invalid")
    if not report["criterion_results"]:
        raise StateTransitionError("evaluation report contains no criteria")
    for criterion in report["criterion_results"]:
        _require_id(criterion.get("criterion_id"), "evaluation criterion ID")
        if criterion.get("outcome") not in {"pass", "fail", "error"} or not isinstance(
            criterion.get("required"), bool
        ):
            raise StateTransitionError("evaluation report criterion outcome is invalid")
        evaluator_refs = criterion.get("evaluator_ids")
        if not isinstance(evaluator_refs, list) or not set(evaluator_refs) <= set(result_ids):
            raise StateTransitionError("evaluation criterion references invalid evaluators")
    regressions = report.get("regressions")
    if not isinstance(regressions, list) or not all(
        isinstance(regression, str) and regression in result_ids for regression in regressions
    ):
        raise StateTransitionError("evaluation report regressions are invalid")
    payload = {key: report[key] for key in required_fields - {"report_id", "fingerprint"}}
    fingerprint = hashlib.sha256(_canonical_json(payload).encode("utf-8")).hexdigest()
    if report.get("fingerprint") != fingerprint:
        raise StateTransitionError("evaluation report fingerprint is invalid")
    if report.get("report_id") != f"evaluation-{fingerprint[:16]}":
        raise StateTransitionError("evaluation report ID is invalid")
    required_criteria = [
        criterion
        for criterion in report.get("criterion_results", [])
        if criterion.get("required")
    ]
    if report["outcome"] == "pass" and (
        not required_criteria
        or any(criterion.get("outcome") != "pass" for criterion in required_criteria)
        or report.get("regressions")
    ):
        raise StateTransitionError("passing evaluation report contradicts its evidence")


def _validate_work_graph(work_items: list[Mapping[str, Any]]) -> None:
    if not isinstance(work_items, list) or not all(
        isinstance(item, Mapping) for item in work_items
    ):
        raise StateTransitionError("work items must be an array of objects")
    ids = [_require_id(item.get("id"), "work-item ID") for item in work_items]
    if not ids:
        raise StateTransitionError("run requires at least one work item")
    if len(ids) != len(set(ids)):
        raise StateTransitionError("duplicate work-item ID")
    known = set(ids)
    graph: dict[str, list[str]] = {}
    for item in work_items:
        dependencies = item.get("depends_on", [])
        if not isinstance(dependencies, list):
            raise StateTransitionError(f"depends_on must be an array for {item['id']}")
        if len(dependencies) != len(set(dependencies)):
            raise StateTransitionError(f"duplicate dependency for {item['id']}")
        for dependency in dependencies:
            _require_id(dependency, f"dependency ID for {item['id']}")
        missing = set(dependencies) - known
        if missing:
            raise StateTransitionError(
                f"work item {item['id']} has missing dependencies: "
                + ", ".join(sorted(missing))
            )
        if item["id"] in dependencies:
            raise StateTransitionError(f"work item {item['id']} depends on itself")
        graph[item["id"]] = list(dependencies)

    visiting: set[str] = set()
    visited: set[str] = set()

    def visit(item_id: str) -> None:
        if item_id in visiting:
            raise StateTransitionError("work-item dependency graph contains a cycle")
        if item_id in visited:
            return
        visiting.add(item_id)
        for dependency in graph[item_id]:
            visit(dependency)
        visiting.remove(item_id)
        visited.add(item_id)

    for item_id in ids:
        visit(item_id)


def reduce_events(events: list[Mapping[str, Any]]) -> dict[str, Any]:
    """Derive current verified state from a validated event sequence."""

    if not events or events[0].get("type") != "run_created":
        raise StateTransitionError("event log must start with run_created")
    created = events[0]
    payload = created["payload"]
    work_items = {
        item["id"]: {
            "id": item["id"],
            "status": "ready" if not item.get("depends_on") else "pending",
            "depends_on": sorted(item.get("depends_on", [])),
            "attempt_count": 0,
            "artifact_refs": [],
            "evidence_refs": [],
            "last_error": None,
        }
        for item in payload["work_items"]
    }
    state = {
        "version": 1,
        "run_id": payload["run_id"],
        "spec_id": payload["spec_id"],
        "status": "planned",
        "work_items": list(work_items.values()),
        "decisions": [],
        "evidence": [],
        "best_known_revision": None,
        "audit_sequence": 0,
        "updated_at": created["recorded_at"],
    }

    for event in events[1:]:
        event_type = event["type"]
        payload = event["payload"]
        item_id = payload.get("work_item_id")
        if item_id not in work_items:
            raise StateTransitionError(f"event references unknown work item: {item_id}")
        item = work_items[item_id]

        if event_type == "work_started":
            if item["status"] != "ready":
                raise StateTransitionError(
                    f"cannot start {item_id} from {item['status']}"
                )
            item["status"] = "running"
            item["attempt_count"] += 1
            item["last_error"] = None
        elif event_type == "executor_submitted":
            if item["status"] != "running":
                raise StateTransitionError(
                    f"cannot submit {item_id} from {item['status']}"
                )
            item["status"] = "awaiting_audit"
            item["artifact_refs"] = sorted(set(payload.get("artifact_refs", [])))
        elif event_type == "evaluation_recorded":
            if item["status"] != "awaiting_audit":
                raise StateTransitionError(
                    f"cannot audit {item_id} from {item['status']}"
                )
            report = payload["report"]
            _validate_evaluation_report(report)
            if report.get("work_item_id") != item_id:
                raise StateTransitionError("evaluation report work item does not match")
            if report.get("spec_id") != state["spec_id"]:
                raise StateTransitionError("evaluation report specification does not match")
            evidence_refs = []
            for result in report.get("evaluator_results", []):
                evidence_id = f"{report['report_id']}.{result['evaluator_id']}"
                if any(evidence["id"] == evidence_id for evidence in state["evidence"]):
                    raise StateTransitionError(f"duplicate evaluation evidence: {evidence_id}")
                evidence_refs.append(evidence_id)
                state["evidence"].append(
                    {
                        "id": evidence_id,
                        "evaluator_id": result["evaluator_id"],
                        "outcome": result["outcome"],
                        "artifact_refs": result.get("artifact_refs", [])
                        or [f"evaluation:{report['report_id']}"],
                        "recorded_at": event["recorded_at"],
                    }
                )
            item["evidence_refs"] = sorted(evidence_refs)
            state["audit_sequence"] += 1
            if report.get("outcome") == "pass" and not report.get("regressions"):
                item["status"] = "verified"
                item["last_error"] = None
                state["best_known_revision"] = payload.get("revision")
            else:
                item["status"] = "rejected"
                item["last_error"] = (
                    f"evaluation {report.get('outcome', 'error')}"
                    + (f"; regressions: {', '.join(report['regressions'])}" if report.get("regressions") else "")
                )
        elif event_type == "work_retried":
            if item["status"] != "rejected":
                raise StateTransitionError(
                    f"cannot retry {item_id} from {item['status']}"
                )
            item["status"] = "ready"
            item["last_error"] = None
        elif event_type == "work_blocked":
            if item["status"] == "verified":
                raise StateTransitionError(f"cannot block verified work item {item_id}")
            item["status"] = "blocked"
            item["last_error"] = payload["reason"]
        else:
            raise StateTransitionError(f"unknown state event type: {event_type}")

        verified = {key for key, value in work_items.items() if value["status"] == "verified"}
        for candidate in work_items.values():
            if candidate["status"] == "pending" and set(candidate["depends_on"]) <= verified:
                candidate["status"] = "ready"
        state["updated_at"] = event["recorded_at"]

    statuses = {item["status"] for item in work_items.values()}
    if statuses == {"verified"}:
        state["status"] = "verified"
    elif "blocked" in statuses:
        state["status"] = "blocked"
    elif "rejected" in statuses:
        state["status"] = "rejected"
    elif statuses & {"running", "awaiting_audit"}:
        state["status"] = "running"
    else:
        state["status"] = "planned"
    state["work_items"] = sorted(work_items.values(), key=lambda item: item["id"])
    state["evidence"] = sorted(state["evidence"], key=lambda item: item["id"])
    return state


class VerifiedStateStore:
    """A single-writer JSONL event store with a tamper-evident hash chain."""

    def __init__(self, path: Path):
        self.path = Path(path)

    def events(self) -> list[dict[str, Any]]:
        if not self.path.exists():
            return []
        try:
            events = [
                json.loads(line)
                for line in self.path.read_text(encoding="utf-8").splitlines()
                if line.strip()
            ]
        except (OSError, UnicodeError, json.JSONDecodeError) as error:
            raise StateTransitionError("event log is not valid UTF-8 JSONL") from error
        previous_hash = GENESIS_HASH
        for sequence, event in enumerate(events, start=1):
            if event.get("sequence") != sequence:
                raise StateTransitionError("event sequence is not contiguous")
            if event.get("previous_hash") != previous_hash:
                raise StateTransitionError("event hash chain is broken")
            supplied_hash = event.get("hash")
            content = {key: value for key, value in event.items() if key != "hash"}
            if supplied_hash != _event_hash(content):
                raise StateTransitionError("event hash is invalid")
            previous_hash = supplied_hash
        return events

    def state(self) -> dict[str, Any]:
        return reduce_events(self.events())

    def create(
        self,
        run_id: str,
        spec_id: str,
        work_items: list[Mapping[str, Any]],
        recorded_at: str,
    ) -> dict[str, Any]:
        if self.path.exists() and self.path.stat().st_size:
            raise StateTransitionError("state store already exists")
        _parse_timestamp(recorded_at)
        _require_id(run_id, "run ID")
        _require_id(spec_id, "specification ID")
        _validate_work_graph(work_items)
        self._append(
            "run_created",
            {
                "run_id": run_id,
                "spec_id": spec_id,
                "work_items": deepcopy(work_items),
            },
            recorded_at,
        )
        return self.state()

    def start(self, work_item_id: str, recorded_at: str) -> dict[str, Any]:
        return self._transition("work_started", {"work_item_id": work_item_id}, recorded_at)

    def submit(
        self,
        work_item_id: str,
        artifact_refs: list[str],
        claim: str,
        recorded_at: str,
    ) -> dict[str, Any]:
        _require_id(work_item_id, "work-item ID")
        if not isinstance(artifact_refs, list) or not all(
            isinstance(reference, str) and reference for reference in artifact_refs
        ):
            raise StateTransitionError("artifact references must be non-empty strings")
        if not isinstance(claim, str) or not claim:
            raise StateTransitionError("executor claim must be a non-empty string")
        return self._transition(
            "executor_submitted",
            {"work_item_id": work_item_id, "artifact_refs": artifact_refs, "claim": claim},
            recorded_at,
        )

    def record_evaluation(
        self,
        work_item_id: str,
        report: Mapping[str, Any],
        revision: str,
        recorded_at: str,
    ) -> dict[str, Any]:
        _require_id(work_item_id, "work-item ID")
        if not isinstance(report, Mapping):
            raise StateTransitionError("evaluation report must be an object")
        _require_id(revision, "revision ID")
        return self._transition(
            "evaluation_recorded",
            {
                "work_item_id": work_item_id,
                "report": deepcopy(dict(report)),
                "revision": revision,
            },
            recorded_at,
        )

    def retry(self, work_item_id: str, recorded_at: str) -> dict[str, Any]:
        return self._transition("work_retried", {"work_item_id": work_item_id}, recorded_at)

    def block(self, work_item_id: str, reason: str, recorded_at: str) -> dict[str, Any]:
        if not isinstance(reason, str) or not reason:
            raise StateTransitionError("block reason must be a non-empty string")
        return self._transition(
            "work_blocked", {"work_item_id": work_item_id, "reason": reason}, recorded_at
        )

    def _transition(
        self, event_type: str, payload: Mapping[str, Any], recorded_at: str
    ) -> dict[str, Any]:
        _parse_timestamp(recorded_at)
        events = self.events()
        if not events:
            raise StateTransitionError("state store has not been created")
        candidate = self._build_event(event_type, payload, recorded_at, events)
        reduce_events([*events, candidate])
        self._write_event(candidate)
        return self.state()

    def _append(
        self, event_type: str, payload: Mapping[str, Any], recorded_at: str
    ) -> None:
        events = self.events()
        candidate = self._build_event(event_type, payload, recorded_at, events)
        self._write_event(candidate)

    def _build_event(
        self,
        event_type: str,
        payload: Mapping[str, Any],
        recorded_at: str,
        events: list[Mapping[str, Any]],
    ) -> dict[str, Any]:
        current_timestamp = _parse_timestamp(recorded_at)
        if events and current_timestamp < _parse_timestamp(events[-1]["recorded_at"]):
            raise StateTransitionError("event timestamps must be monotonic")
        content = {
            "version": 1,
            "sequence": len(events) + 1,
            "type": event_type,
            "recorded_at": recorded_at,
            "previous_hash": events[-1]["hash"] if events else GENESIS_HASH,
            "payload": deepcopy(dict(payload)),
        }
        return {**content, "hash": _event_hash(content)}

    def _write_event(self, event: Mapping[str, Any]) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("a", encoding="utf-8", newline="\n") as handle:
            handle.write(_canonical_json(event) + "\n")
            handle.flush()
            os.fsync(handle.fileno())
