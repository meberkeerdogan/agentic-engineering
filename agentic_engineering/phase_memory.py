"""Bounded, provenance-preserving phase-aware memory views."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any


class PhaseMemoryError(ValueError):
    """Raised when memory provenance, bounds, or queries are invalid."""


PHASES = ("navigate", "reproduce", "patch", "validate", "complete")
KINDS = {"decision", "failure", "artifact", "evidence"}
ID_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")
PHASE_CONTEXT = {
    "navigate": {"navigate"},
    "reproduce": {"navigate", "reproduce"},
    "patch": {"reproduce", "patch"},
    "validate": {"patch", "validate"},
    "complete": {"validate", "complete"},
}


def _canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"), sort_keys=True)


def _fingerprint(value: Any) -> str:
    return hashlib.sha256(_canonical_json(value).encode("utf-8")).hexdigest()


def _refs(value: Any) -> bool:
    return (
        isinstance(value, list)
        and bool(value)
        and all(isinstance(item, str) and item for item in value)
        and len(value) == len(set(value))
    )


def build_memory_view(manifest: Mapping[str, Any]) -> dict[str, Any]:
    """Apply supersession, phase bounds, and deterministic query ranking."""

    if manifest.get("version") != 1 or not isinstance(manifest.get("memory_id"), str):
        raise PhaseMemoryError("memory must use version 1 and a memory ID")
    if not ID_PATTERN.fullmatch(manifest["memory_id"]):
        raise PhaseMemoryError("memory ID must be path-safe")
    capacity = manifest.get("capacity_per_phase")
    entries = manifest.get("entries")
    query = manifest.get("query")
    if isinstance(capacity, bool) or not isinstance(capacity, int) or capacity < 1:
        raise PhaseMemoryError("capacity_per_phase must be positive")
    if not isinstance(entries, list) or not isinstance(query, Mapping):
        raise PhaseMemoryError("entries and query are required")
    normalized: dict[str, dict[str, Any]] = {}
    for entry in entries:
        if not isinstance(entry, Mapping) or not isinstance(entry.get("id"), str):
            raise PhaseMemoryError("memory entries require IDs")
        entry_id = entry["id"]
        if entry_id in normalized or not ID_PATTERN.fullmatch(entry_id):
            raise PhaseMemoryError("memory entry IDs must be unique and path-safe")
        if entry.get("phase") not in PHASES or entry.get("kind") not in KINDS:
            raise PhaseMemoryError("memory entry phase or kind is unsupported")
        if not isinstance(entry.get("task_id"), str) or not ID_PATTERN.fullmatch(entry["task_id"]):
            raise PhaseMemoryError("memory task IDs must be path-safe")
        if not isinstance(entry.get("summary"), str) or not entry["summary"]:
            raise PhaseMemoryError("memory summaries must be non-empty")
        step = entry.get("created_step")
        if isinstance(step, bool) or not isinstance(step, int) or step < 1:
            raise PhaseMemoryError("memory steps must be positive integers")
        if not _refs(entry.get("evidence_refs")):
            raise PhaseMemoryError("memory entries require unique evidence references")
        supersedes = entry.get("supersedes")
        if supersedes is not None and not isinstance(supersedes, str):
            raise PhaseMemoryError("supersedes must be an entry ID or null")
        normalized[entry_id] = dict(entry)
    superseded: set[str] = set()
    for entry in normalized.values():
        target_id = entry.get("supersedes")
        if target_id is None:
            continue
        target = normalized.get(target_id)
        if target is None or target_id == entry["id"]:
            raise PhaseMemoryError("supersedes must reference another declared entry")
        if target["task_id"] != entry["task_id"] or target["created_step"] >= entry["created_step"]:
            raise PhaseMemoryError("supersession requires an older entry for the same task")
        superseded.add(target_id)
    active = [entry for entry in normalized.values() if entry["id"] not in superseded]
    retained: list[dict[str, Any]] = []
    evicted: list[str] = []
    for phase in PHASES:
        phase_entries = sorted(
            (entry for entry in active if entry["phase"] == phase),
            key=lambda item: (-item["created_step"], item["id"]),
        )
        retained.extend(phase_entries[:capacity])
        evicted.extend(entry["id"] for entry in phase_entries[capacity:])
    retained.sort(key=lambda item: (item["created_step"], item["id"]))
    phase = query.get("phase")
    task_id = query.get("task_id")
    limit = query.get("limit")
    kinds = query.get("kinds")
    if phase not in PHASES or not isinstance(task_id, str) or not ID_PATTERN.fullmatch(task_id):
        raise PhaseMemoryError("query phase and task ID are invalid")
    if isinstance(limit, bool) or not isinstance(limit, int) or limit < 1:
        raise PhaseMemoryError("query limit must be positive")
    if (
        not isinstance(kinds, list)
        or not kinds
        or len(kinds) != len(set(kinds))
        or any(kind not in KINDS for kind in kinds)
    ):
        raise PhaseMemoryError("query kinds must be supported")
    candidates = [
        entry
        for entry in retained
        if entry["kind"] in kinds and entry["phase"] in PHASE_CONTEXT[phase]
    ]
    candidates.sort(
        key=lambda entry: (
            -(4 if entry["task_id"] == task_id else 0),
            -(2 if entry["phase"] == phase else 1),
            -entry["created_step"],
            entry["id"],
        )
    )
    report: dict[str, Any] = {
        "version": 1,
        "memory_id": manifest["memory_id"],
        "source_fingerprint": _fingerprint(manifest),
        "capacity_per_phase": capacity,
        "retained_entry_ids": [entry["id"] for entry in retained],
        "superseded_entry_ids": sorted(superseded),
        "evicted_entry_ids": sorted(evicted),
        "retrieved_entries": candidates[:limit],
        "writes": [],
        "state_mutations": [],
    }
    fingerprint = _fingerprint(report)
    report["report_id"] = f"phase-memory-{fingerprint[:16]}"
    report["fingerprint"] = fingerprint
    return report


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    arguments = parser.parse_args(argv)
    report = build_memory_view(json.loads(arguments.manifest.read_text("utf-8")))
    arguments.output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
