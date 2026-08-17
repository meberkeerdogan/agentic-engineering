"""Validate an offline M07d bounded phase-memory evidence campaign."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

from .phase_memory import PhaseMemoryError, build_memory_view
from .task_pack import TaskPackError, validate_task_pack


class MemoryCampaignError(ValueError):
    """Raised when the phase-memory campaign is not trustworthy."""


ID_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")
POLICY_START = "<!-- memory-policy:start -->"
POLICY_END = "<!-- memory-policy:end -->"
PRESSURE_SHAPES = {"low", "supersession", "eviction"}
CAMPAIGN_FIELDS = {
    "version",
    "campaign_id",
    "title",
    "task_pack_ref",
    "control_arm_id",
    "treatment_arm_id",
    "control_workflow_ref",
    "memory_workflow_ref",
    "requirements",
    "task_memories",
    "model_execution_allowed",
}
REQUIREMENT_FIELDS = {
    "minimum_tasks",
    "minimum_distinct_repositories",
    "minimum_seeds",
    "required_pressure_shapes",
    "minimum_pressure_tasks",
    "minimum_negative_controls",
}
TASK_MEMORY_FIELDS = {
    "id",
    "pressure_shape",
    "memory_ref",
    "expected_retrieved_entry_ids",
    "expected_superseded_entry_ids",
    "expected_evicted_entry_ids",
}


def _canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"), sort_keys=True)


def _fingerprint(value: Any) -> str:
    return hashlib.sha256(_canonical_json(value).encode("utf-8")).hexdigest()


def _load_object(path: Path, label: str) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        raise MemoryCampaignError(f"{label} is not valid UTF-8 JSON") from error
    if not isinstance(value, dict):
        raise MemoryCampaignError(f"{label} must be a JSON object")
    return value


def _resolve_inside(root: Path, reference: Any, label: str) -> Path:
    if not isinstance(reference, str) or not reference:
        raise MemoryCampaignError(f"{label} must be a non-empty relative path")
    path = Path(reference)
    if path.is_absolute() or ".." in path.parts:
        raise MemoryCampaignError(f"{label} must be relative")
    root = root.resolve()
    current = root
    for part in path.parts:
        current /= part
        if current.is_symlink() or getattr(current, "is_junction", lambda: False)():
            raise MemoryCampaignError(f"{label} may not cross a filesystem link")
    candidate = (root / path).resolve()
    try:
        candidate.relative_to(root)
    except ValueError as error:
        raise MemoryCampaignError(f"{label} escapes its root") from error
    return candidate


def _id_list(value: Any, label: str, *, non_empty: bool = False) -> list[str]:
    if (
        not isinstance(value, list)
        or (non_empty and not value)
        or any(not isinstance(item, str) or not ID_PATTERN.fullmatch(item) for item in value)
        or len(value) != len(set(value))
    ):
        qualifier = "non-empty " if non_empty else ""
        raise MemoryCampaignError(f"{label} must be a {qualifier}unique ID array")
    return value


def _split_workflow(path: Path) -> tuple[str, str]:
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as error:
        raise MemoryCampaignError("workflow is not readable UTF-8") from error
    if text.count(POLICY_START) != 1 or text.count(POLICY_END) != 1:
        raise MemoryCampaignError("workflow must contain one memory-policy block")
    before, remainder = text.split(POLICY_START, 1)
    policy, after = remainder.split(POLICY_END, 1)
    policy = policy.strip()
    common = (before + after).strip()
    if not policy or not common:
        raise MemoryCampaignError("workflow policy and shared core must be non-empty")
    return policy, common


def _validate_manifest(value: Mapping[str, Any]) -> None:
    if set(value) != CAMPAIGN_FIELDS or value.get("version") != 1:
        raise MemoryCampaignError("campaign must contain exactly the version 1 fields")
    for field in (
        "campaign_id",
        "title",
        "task_pack_ref",
        "control_arm_id",
        "treatment_arm_id",
        "control_workflow_ref",
        "memory_workflow_ref",
    ):
        if not isinstance(value.get(field), str) or not value[field]:
            raise MemoryCampaignError(f"{field} must be a non-empty string")
    for field in ("campaign_id", "control_arm_id", "treatment_arm_id"):
        if not ID_PATTERN.fullmatch(value[field]):
            raise MemoryCampaignError(f"{field} must be path-safe")
    if value["control_arm_id"] == value["treatment_arm_id"]:
        raise MemoryCampaignError("control and treatment arms must differ")
    if value["control_workflow_ref"] == value["memory_workflow_ref"]:
        raise MemoryCampaignError("workflow references must differ")
    if value.get("model_execution_allowed") is not False:
        raise MemoryCampaignError("campaign readiness must prohibit model execution")

    requirements = value.get("requirements")
    if not isinstance(requirements, Mapping) or set(requirements) != REQUIREMENT_FIELDS:
        raise MemoryCampaignError("campaign requirement fields are invalid")
    for field in (
        "minimum_tasks",
        "minimum_distinct_repositories",
        "minimum_seeds",
        "minimum_pressure_tasks",
        "minimum_negative_controls",
    ):
        number = requirements.get(field)
        if isinstance(number, bool) or not isinstance(number, int) or number < 1:
            raise MemoryCampaignError(f"{field} must be a positive integer")
    shapes = requirements.get("required_pressure_shapes")
    if not isinstance(shapes, list) or set(shapes) != PRESSURE_SHAPES or len(shapes) != 3:
        raise MemoryCampaignError(
            "required pressure shapes must be low, supersession, and eviction"
        )

    records = value.get("task_memories")
    if not isinstance(records, list) or not records:
        raise MemoryCampaignError("campaign requires task memories")
    identifiers: list[str] = []
    for record in records:
        if not isinstance(record, Mapping) or set(record) != TASK_MEMORY_FIELDS:
            raise MemoryCampaignError("task-memory fields are invalid")
        task_id = record.get("id")
        if not isinstance(task_id, str) or not ID_PATTERN.fullmatch(task_id):
            raise MemoryCampaignError("task-memory IDs must be path-safe")
        identifiers.append(task_id)
        shape = record.get("pressure_shape")
        if shape not in PRESSURE_SHAPES:
            raise MemoryCampaignError("task-memory pressure shape is invalid")
        if not isinstance(record.get("memory_ref"), str) or not record["memory_ref"]:
            raise MemoryCampaignError("task-memory reference must be non-empty")
        retrieved = _id_list(
            record.get("expected_retrieved_entry_ids"),
            "expected_retrieved_entry_ids",
            non_empty=True,
        )
        superseded = _id_list(
            record.get("expected_superseded_entry_ids"),
            "expected_superseded_entry_ids",
        )
        evicted = _id_list(
            record.get("expected_evicted_entry_ids"), "expected_evicted_entry_ids"
        )
        if not retrieved:
            raise MemoryCampaignError("each task must retrieve memory")
        if shape == "low" and (superseded or evicted):
            raise MemoryCampaignError("low-pressure controls may not discard entries")
        if shape == "supersession" and not superseded:
            raise MemoryCampaignError("supersession tasks must discard an older entry")
        if shape == "eviction" and not evicted:
            raise MemoryCampaignError("eviction tasks must exceed a phase bound")
    if len(identifiers) != len(set(identifiers)):
        raise MemoryCampaignError("task-memory IDs must be unique")


def _validate_evidence_files(repository: Path, memory: Mapping[str, Any]) -> None:
    for entry in memory.get("entries", []):
        if not isinstance(entry, Mapping):
            continue
        for reference in entry.get("evidence_refs", []):
            evidence = _resolve_inside(repository, reference, "memory evidence reference")
            if not evidence.is_file():
                raise MemoryCampaignError("memory evidence reference does not exist")


def validate_memory_campaign(project_root: Path, manifest_path: Path) -> dict[str, Any]:
    """Validate memory-campaign readiness without model calls or task mutation."""

    project_root = project_root.resolve()
    if not project_root.is_dir():
        raise MemoryCampaignError("project root does not exist")
    manifest_path = manifest_path.resolve()
    try:
        manifest_path.relative_to(project_root)
    except ValueError as error:
        raise MemoryCampaignError("campaign manifest must be inside the project root") from error
    manifest = _load_object(manifest_path, "campaign manifest")
    _validate_manifest(manifest)

    task_pack_path = _resolve_inside(
        project_root, manifest["task_pack_ref"], "task-pack reference"
    )
    try:
        readiness = validate_task_pack(project_root, task_pack_path)
    except TaskPackError as error:
        raise MemoryCampaignError(f"task pack is not ready: {error}") from error
    task_pack = _load_object(task_pack_path, "task-pack manifest")
    experiment_path = _resolve_inside(
        project_root, task_pack.get("experiment_ref"), "experiment reference"
    )
    experiment = _load_object(experiment_path, "experiment plan")
    treatments = experiment.get("treatments", [])
    if (
        experiment.get("control", {}).get("id") != manifest["control_arm_id"]
        or len(treatments) != 1
        or treatments[0].get("id") != manifest["treatment_arm_id"]
        or experiment["control"].get("config_ref") != manifest["control_workflow_ref"]
        or treatments[0].get("config_ref") != manifest["memory_workflow_ref"]
    ):
        raise MemoryCampaignError("experiment arms do not match the campaign")

    requirements = manifest["requirements"]
    if readiness["task_count"] < requirements["minimum_tasks"]:
        raise MemoryCampaignError("campaign has too few tasks")
    if readiness["distinct_repository_count"] < requirements["minimum_distinct_repositories"]:
        raise MemoryCampaignError("campaign has too few distinct repositories")
    if readiness["seed_count"] < requirements["minimum_seeds"]:
        raise MemoryCampaignError("campaign has too few repeated seeds")
    task_by_id = {task["id"]: task for task in experiment["tasks"]}
    memory_by_id = {record["id"]: record for record in manifest["task_memories"]}
    if set(task_by_id) != set(memory_by_id):
        raise MemoryCampaignError("task memories must exactly match experiment tasks")
    if {record["pressure_shape"] for record in memory_by_id.values()} != PRESSURE_SHAPES:
        raise MemoryCampaignError("campaign must cover every required pressure shape")

    shared_cores: set[str] = set()
    control_policies: set[str] = set()
    memory_policies: set[str] = set()
    task_results: list[dict[str, Any]] = []
    for task_id in sorted(task_by_id):
        task = task_by_id[task_id]
        record = memory_by_id[task_id]
        repository = _resolve_inside(
            project_root, task["repository"], "task repository reference"
        )
        control_path = _resolve_inside(
            repository, manifest["control_workflow_ref"], "control workflow reference"
        )
        memory_path = _resolve_inside(
            repository, manifest["memory_workflow_ref"], "memory workflow reference"
        )
        if not control_path.is_file() or not memory_path.is_file():
            raise MemoryCampaignError("campaign workflow is missing")
        control_policy, control_core = _split_workflow(control_path)
        memory_policy, memory_core = _split_workflow(memory_path)
        if control_policy == memory_policy or control_core != memory_core:
            raise MemoryCampaignError("arms must differ only in memory policy")
        shared_cores.add(_fingerprint(control_core))
        control_policies.add(_fingerprint(control_policy))
        memory_policies.add(_fingerprint(memory_policy))

        memory_path = _resolve_inside(repository, record["memory_ref"], "memory reference")
        memory = _load_object(memory_path, "phase-memory manifest")
        try:
            report = build_memory_view(memory)
        except PhaseMemoryError as error:
            raise MemoryCampaignError(f"phase memory is invalid: {error}") from error
        _validate_evidence_files(repository, memory)
        if report["writes"] or report["state_mutations"]:
            raise MemoryCampaignError("memory reports must remain read-only")
        retrieved_ids = [entry["id"] for entry in report["retrieved_entries"]]
        if retrieved_ids != record["expected_retrieved_entry_ids"]:
            raise MemoryCampaignError(f"retrieved entries changed for task {task_id}")
        if report["superseded_entry_ids"] != record["expected_superseded_entry_ids"]:
            raise MemoryCampaignError(f"superseded entries changed for task {task_id}")
        if report["evicted_entry_ids"] != record["expected_evicted_entry_ids"]:
            raise MemoryCampaignError(f"evicted entries changed for task {task_id}")
        query_task = memory.get("query", {}).get("task_id")
        current_task_count = sum(
            entry.get("task_id") == query_task for entry in report["retrieved_entries"]
        )
        if current_task_count < 1:
            raise MemoryCampaignError("memory view must retrieve current-task evidence")
        task_results.append(
            {
                "id": task_id,
                "pressure_shape": record["pressure_shape"],
                "repository": task["repository"],
                "memory_source_fingerprint": report["source_fingerprint"],
                "memory_report_fingerprint": report["fingerprint"],
                "retrieved_entry_ids": retrieved_ids,
                "superseded_entry_ids": report["superseded_entry_ids"],
                "evicted_entry_ids": report["evicted_entry_ids"],
                "current_task_retrieval_count": current_task_count,
            }
        )
    if len(shared_cores) != 1 or len(control_policies) != 1 or len(memory_policies) != 1:
        raise MemoryCampaignError("all tasks must receive the same isolated workflow factor")

    pressure_count = sum(result["pressure_shape"] != "low" for result in task_results)
    negative_controls = len(task_results) - pressure_count
    if pressure_count < requirements["minimum_pressure_tasks"]:
        raise MemoryCampaignError("campaign has too few memory-pressure tasks")
    if negative_controls < requirements["minimum_negative_controls"]:
        raise MemoryCampaignError("campaign has too few negative controls")

    payload: dict[str, Any] = {
        "version": 1,
        "campaign_id": manifest["campaign_id"],
        "status": "ready_for_separate_approval",
        "campaign_fingerprint": _fingerprint(manifest),
        "task_pack_readiness_fingerprint": readiness["fingerprint"],
        "experiment_id": experiment["experiment_id"],
        "experiment_plan_fingerprint": readiness["plan_fingerprint"],
        "shared_workflow_core_fingerprint": next(iter(shared_cores)),
        "control_policy_fingerprint": next(iter(control_policies)),
        "memory_policy_fingerprint": next(iter(memory_policies)),
        "task_count": readiness["task_count"],
        "seed_count": readiness["seed_count"],
        "arm_count": readiness["arm_count"],
        "matrix_size": readiness["matrix_size"],
        "pressure_task_count": pressure_count,
        "negative_control_count": negative_controls,
        "model_calls_performed": False,
        "paid_execution_authorized": False,
        "tasks": task_results,
    }
    fingerprint = _fingerprint(payload)
    return {
        **payload,
        "report_id": f"memory-campaign-readiness-{fingerprint[:16]}",
        "fingerprint": fingerprint,
    }


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest", type=Path)
    parser.add_argument("--project-root", type=Path, default=Path.cwd())
    parser.add_argument("--output", "-o", type=Path)
    arguments = parser.parse_args(argv)
    report = validate_memory_campaign(arguments.project_root, arguments.manifest)
    output = json.dumps(report, ensure_ascii=False, indent=2) + "\n"
    if arguments.output:
        arguments.output.write_text(output, encoding="utf-8")
    else:
        sys.stdout.write(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
