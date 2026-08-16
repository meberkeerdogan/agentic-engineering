"""Validate an offline M07c static-versus-adaptive planning campaign."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

from .dependency_planning import DependencyPlanError, build_dependency_plan
from .task_pack import TaskPackError, validate_task_pack


class PlanningCampaignError(ValueError):
    """Raised when the dependency-planning campaign is not trustworthy."""


ID_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")
POLICY_START = "<!-- planning-policy:start -->"
POLICY_END = "<!-- planning-policy:end -->"
CAMPAIGN_FIELDS = {
    "version",
    "campaign_id",
    "title",
    "task_pack_ref",
    "control_arm_id",
    "treatment_arm_id",
    "static_workflow_ref",
    "adaptive_workflow_ref",
    "requirements",
    "task_plans",
    "model_execution_allowed",
}
REQUIREMENT_FIELDS = {
    "minimum_tasks",
    "minimum_distinct_repositories",
    "minimum_seeds",
    "required_graph_shapes",
    "minimum_divergent_plans",
    "minimum_negative_controls",
}
TASK_PLAN_FIELDS = {
    "id",
    "graph_shape",
    "plan_ref",
    "expected_static_order",
    "expected_adaptive_order",
    "expected_ready_task_ids",
    "expected_blocked_task_ids",
    "expected_plan_divergence",
}
GRAPH_SHAPES = {"chain", "fan-out", "diamond"}


def _canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"), sort_keys=True)


def _fingerprint(value: Any) -> str:
    return hashlib.sha256(_canonical_json(value).encode("utf-8")).hexdigest()


def _load_object(path: Path, label: str) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        raise PlanningCampaignError(f"{label} is not valid UTF-8 JSON") from error
    if not isinstance(value, dict):
        raise PlanningCampaignError(f"{label} must be a JSON object")
    return value


def _resolve_inside(root: Path, reference: Any, label: str) -> Path:
    if not isinstance(reference, str) or not reference:
        raise PlanningCampaignError(f"{label} must be a non-empty relative path")
    path = Path(reference)
    if path.is_absolute() or ".." in path.parts:
        raise PlanningCampaignError(f"{label} must be relative")
    root = root.resolve()
    lexical = root / path
    current = root
    for part in path.parts:
        current /= part
        if current.is_symlink() or getattr(current, "is_junction", lambda: False)():
            raise PlanningCampaignError(f"{label} may not cross a filesystem link")
    candidate = lexical.resolve()
    try:
        candidate.relative_to(root)
    except ValueError as error:
        raise PlanningCampaignError(f"{label} escapes its root") from error
    return candidate


def _id_list(value: Any, label: str) -> list[str]:
    if (
        not isinstance(value, list)
        or any(
            not isinstance(item, str) or not ID_PATTERN.fullmatch(item)
            for item in value
        )
        or len(value) != len(set(value))
    ):
        raise PlanningCampaignError(f"{label} must be a unique ID array")
    return value


def _split_workflow(path: Path) -> tuple[str, str]:
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as error:
        raise PlanningCampaignError("workflow is not readable UTF-8") from error
    if text.count(POLICY_START) != 1 or text.count(POLICY_END) != 1:
        raise PlanningCampaignError("workflow must contain one planning-policy block")
    before, remainder = text.split(POLICY_START, 1)
    policy, after = remainder.split(POLICY_END, 1)
    policy = policy.strip()
    common = (before + after).strip()
    if not policy or not common:
        raise PlanningCampaignError("workflow policy and shared core must be non-empty")
    return policy, common


def _validate_manifest(value: Mapping[str, Any]) -> None:
    if set(value) != CAMPAIGN_FIELDS or value.get("version") != 1:
        raise PlanningCampaignError("campaign must contain exactly the version 1 fields")
    for field in (
        "campaign_id",
        "title",
        "task_pack_ref",
        "control_arm_id",
        "treatment_arm_id",
        "static_workflow_ref",
        "adaptive_workflow_ref",
    ):
        if not isinstance(value.get(field), str) or not value[field]:
            raise PlanningCampaignError(f"{field} must be a non-empty string")
    for field in ("campaign_id", "control_arm_id", "treatment_arm_id"):
        if not ID_PATTERN.fullmatch(value[field]):
            raise PlanningCampaignError(f"{field} must be path-safe")
    if value["control_arm_id"] == value["treatment_arm_id"]:
        raise PlanningCampaignError("control and treatment arms must differ")
    if value["static_workflow_ref"] == value["adaptive_workflow_ref"]:
        raise PlanningCampaignError("workflow references must differ")
    if value.get("model_execution_allowed") is not False:
        raise PlanningCampaignError("campaign readiness must prohibit model execution")
    requirements = value.get("requirements")
    if not isinstance(requirements, Mapping) or set(requirements) != REQUIREMENT_FIELDS:
        raise PlanningCampaignError("campaign requirement fields are invalid")
    for field in (
        "minimum_tasks",
        "minimum_distinct_repositories",
        "minimum_seeds",
        "minimum_divergent_plans",
        "minimum_negative_controls",
    ):
        number = requirements.get(field)
        if isinstance(number, bool) or not isinstance(number, int) or number < 1:
            raise PlanningCampaignError(f"{field} must be a positive integer")
    shapes = requirements.get("required_graph_shapes")
    if not isinstance(shapes, list) or set(shapes) != GRAPH_SHAPES or len(shapes) != 3:
        raise PlanningCampaignError("required graph shapes must be chain, fan-out, and diamond")
    records = value.get("task_plans")
    if not isinstance(records, list) or not records:
        raise PlanningCampaignError("campaign requires task plans")
    identifiers: list[str] = []
    for record in records:
        if not isinstance(record, Mapping) or set(record) != TASK_PLAN_FIELDS:
            raise PlanningCampaignError("task-plan fields are invalid")
        task_id = record.get("id")
        if not isinstance(task_id, str) or not ID_PATTERN.fullmatch(task_id):
            raise PlanningCampaignError("task-plan IDs must be path-safe")
        identifiers.append(task_id)
        if record.get("graph_shape") not in GRAPH_SHAPES:
            raise PlanningCampaignError("task-plan graph shape is invalid")
        if not isinstance(record.get("plan_ref"), str) or not record["plan_ref"]:
            raise PlanningCampaignError("task-plan reference must be non-empty")
        for field in (
            "expected_static_order",
            "expected_adaptive_order",
            "expected_ready_task_ids",
            "expected_blocked_task_ids",
        ):
            _id_list(record.get(field), field)
        if not isinstance(record.get("expected_plan_divergence"), bool):
            raise PlanningCampaignError("expected plan divergence must be boolean")
    if len(identifiers) != len(set(identifiers)):
        raise PlanningCampaignError("task-plan IDs must be unique")


def _validate_evidence_files(repository: Path, plan: Mapping[str, Any]) -> None:
    records = [*plan.get("tasks", []), *plan.get("runtime_states", [])]
    for record in records:
        if not isinstance(record, Mapping):
            continue
        for reference in record.get("evidence_refs", []):
            evidence = _resolve_inside(repository, reference, "plan evidence reference")
            if not evidence.is_file():
                raise PlanningCampaignError("plan evidence reference does not exist")


def validate_planning_campaign(
    project_root: Path, manifest_path: Path
) -> dict[str, Any]:
    """Validate campaign readiness without invoking an agent or changing task state."""

    project_root = project_root.resolve()
    if not project_root.is_dir():
        raise PlanningCampaignError("project root does not exist")
    manifest_path = manifest_path.resolve()
    try:
        manifest_path.relative_to(project_root)
    except ValueError as error:
        raise PlanningCampaignError(
            "campaign manifest must be inside the project root"
        ) from error
    manifest = _load_object(manifest_path, "campaign manifest")
    _validate_manifest(manifest)

    task_pack_path = _resolve_inside(
        project_root, manifest["task_pack_ref"], "task-pack reference"
    )
    try:
        readiness = validate_task_pack(project_root, task_pack_path)
    except TaskPackError as error:
        raise PlanningCampaignError(f"task pack is not ready: {error}") from error
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
        or experiment["control"].get("config_ref") != manifest["static_workflow_ref"]
        or treatments[0].get("config_ref") != manifest["adaptive_workflow_ref"]
    ):
        raise PlanningCampaignError("experiment arms do not match the campaign")

    requirements = manifest["requirements"]
    if readiness["task_count"] < requirements["minimum_tasks"]:
        raise PlanningCampaignError("campaign has too few tasks")
    if (
        readiness["distinct_repository_count"]
        < requirements["minimum_distinct_repositories"]
    ):
        raise PlanningCampaignError("campaign has too few distinct repositories")
    if readiness["seed_count"] < requirements["minimum_seeds"]:
        raise PlanningCampaignError("campaign has too few repeated seeds")
    task_by_id = {task["id"]: task for task in experiment["tasks"]}
    plan_by_id = {record["id"]: record for record in manifest["task_plans"]}
    if set(task_by_id) != set(plan_by_id):
        raise PlanningCampaignError("task plans must exactly match experiment tasks")
    if {record["graph_shape"] for record in plan_by_id.values()} != GRAPH_SHAPES:
        raise PlanningCampaignError("campaign must cover every required graph shape")

    shared_cores: set[str] = set()
    static_policies: set[str] = set()
    adaptive_policies: set[str] = set()
    task_results: list[dict[str, Any]] = []
    for task_id in sorted(task_by_id):
        task = task_by_id[task_id]
        record = plan_by_id[task_id]
        repository = _resolve_inside(
            project_root, task["repository"], "task repository reference"
        )
        static_path = _resolve_inside(
            repository, manifest["static_workflow_ref"], "static workflow reference"
        )
        adaptive_path = _resolve_inside(
            repository, manifest["adaptive_workflow_ref"], "adaptive workflow reference"
        )
        if not static_path.is_file() or not adaptive_path.is_file():
            raise PlanningCampaignError("campaign workflow is missing")
        static_policy, static_core = _split_workflow(static_path)
        adaptive_policy, adaptive_core = _split_workflow(adaptive_path)
        if static_policy == adaptive_policy or static_core != adaptive_core:
            raise PlanningCampaignError("arms must differ only in planning policy")
        shared_cores.add(_fingerprint(static_core))
        static_policies.add(_fingerprint(static_policy))
        adaptive_policies.add(_fingerprint(adaptive_policy))

        plan_path = _resolve_inside(
            repository, record["plan_ref"], "dependency plan reference"
        )
        plan = _load_object(plan_path, "dependency plan")
        try:
            static_report = build_dependency_plan(plan, "static")
            adaptive_report = build_dependency_plan(plan, "adaptive")
        except DependencyPlanError as error:
            raise PlanningCampaignError(f"dependency plan is invalid: {error}") from error
        _validate_evidence_files(repository, plan)
        for report in (static_report, adaptive_report):
            if report["executions"] or report["state_mutations"]:
                raise PlanningCampaignError("planning reports must remain read-only")
        if static_report["ordered_task_ids"] != record["expected_static_order"]:
            raise PlanningCampaignError(f"static order changed for task {task_id}")
        if adaptive_report["ordered_task_ids"] != record["expected_adaptive_order"]:
            raise PlanningCampaignError(f"adaptive order changed for task {task_id}")
        if adaptive_report["ready_task_ids"] != record["expected_ready_task_ids"]:
            raise PlanningCampaignError(f"ready frontier changed for task {task_id}")
        if adaptive_report["blocked_task_ids"] != record["expected_blocked_task_ids"]:
            raise PlanningCampaignError(f"blocked tasks changed for task {task_id}")
        divergence = (
            static_report["ordered_task_ids"] != adaptive_report["ordered_task_ids"]
        )
        if divergence is not record["expected_plan_divergence"]:
            raise PlanningCampaignError(f"plan divergence changed for task {task_id}")
        task_results.append(
            {
                "id": task_id,
                "graph_shape": record["graph_shape"],
                "repository": task["repository"],
                "plan_source_fingerprint": static_report["source_fingerprint"],
                "static_report_fingerprint": static_report["fingerprint"],
                "adaptive_report_fingerprint": adaptive_report["fingerprint"],
                "static_order": static_report["ordered_task_ids"],
                "adaptive_order": adaptive_report["ordered_task_ids"],
                "ready_task_ids": adaptive_report["ready_task_ids"],
                "blocked_task_ids": adaptive_report["blocked_task_ids"],
                "plan_divergence": divergence,
            }
        )
    if (
        len(shared_cores) != 1
        or len(static_policies) != 1
        or len(adaptive_policies) != 1
    ):
        raise PlanningCampaignError("all tasks must receive the same isolated workflow factor")
    divergent = sum(result["plan_divergence"] for result in task_results)
    negative_controls = len(task_results) - divergent
    if divergent < requirements["minimum_divergent_plans"]:
        raise PlanningCampaignError("campaign has too few divergent plans")
    if negative_controls < requirements["minimum_negative_controls"]:
        raise PlanningCampaignError("campaign has too few negative controls")

    payload: dict[str, Any] = {
        "version": 1,
        "campaign_id": manifest["campaign_id"],
        "status": "ready_for_separate_approval",
        "campaign_fingerprint": _fingerprint(manifest),
        "task_pack_readiness_fingerprint": readiness["fingerprint"],
        "experiment_id": experiment["experiment_id"],
        "experiment_plan_fingerprint": readiness["plan_fingerprint"],
        "shared_workflow_core_fingerprint": next(iter(shared_cores)),
        "static_policy_fingerprint": next(iter(static_policies)),
        "adaptive_policy_fingerprint": next(iter(adaptive_policies)),
        "task_count": readiness["task_count"],
        "seed_count": readiness["seed_count"],
        "arm_count": readiness["arm_count"],
        "matrix_size": readiness["matrix_size"],
        "divergent_plan_count": divergent,
        "negative_control_count": negative_controls,
        "model_calls_performed": False,
        "paid_execution_authorized": False,
        "tasks": task_results,
    }
    fingerprint = _fingerprint(payload)
    return {
        **payload,
        "report_id": f"planning-campaign-readiness-{fingerprint[:16]}",
        "fingerprint": fingerprint,
    }


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest", type=Path)
    parser.add_argument("--project-root", type=Path, default=Path.cwd())
    parser.add_argument("--output", "-o", type=Path)
    arguments = parser.parse_args(argv)
    report = validate_planning_campaign(arguments.project_root, arguments.manifest)
    output = json.dumps(report, ensure_ascii=False, indent=2) + "\n"
    if arguments.output:
        arguments.output.write_text(output, encoding="utf-8")
    else:
        sys.stdout.write(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
