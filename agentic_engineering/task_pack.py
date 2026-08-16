"""Validate a representative coding-agent task pack without model execution."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import sys
import tempfile
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

from .evaluators import EvaluationError, run_single_pass_baseline
from .experiments import (
    ExperimentError,
    experiment_cells,
    experiment_plan_fingerprint,
    validate_experiment_plan,
)


class TaskPackError(ValueError):
    """Raised when a task pack is not ready for a controlled experiment."""


PACK_FIELDS = {
    "version",
    "pack_id",
    "title",
    "experiment_ref",
    "requirements",
    "task_bindings",
}
REQUIREMENT_FIELDS = {
    "minimum_distinct_repositories",
    "minimum_seeds",
    "required_categories",
}
BINDING_FIELDS = {
    "id",
    "category",
    "evidence_contract_ref",
    "expected_baseline_outcome",
    "expected_failing_evaluator_ids",
}
REQUIRED_CATEGORIES = {
    "bounded-bug-fix",
    "multi-file-feature",
    "multi-step-evolution",
}
ID_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")
SAFE_COMMAND_PREFIX = ["{python}", "-m", "unittest"]


def _canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"), sort_keys=True)


def _fingerprint(value: Any) -> str:
    return hashlib.sha256(_canonical_json(value).encode("utf-8")).hexdigest()


def _load_object(path: Path, label: str) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        raise TaskPackError(f"{label} is not valid UTF-8 JSON") from error
    if not isinstance(value, dict):
        raise TaskPackError(f"{label} must be a JSON object")
    return value


def _resolve_inside(root: Path, reference: Any, label: str) -> Path:
    if not isinstance(reference, str) or not reference:
        raise TaskPackError(f"{label} must be a non-empty relative path")
    path = Path(reference)
    if path.is_absolute():
        raise TaskPackError(f"{label} must be relative to the project root")
    root = root.resolve()
    candidate = (root / path).resolve()
    try:
        candidate.relative_to(root)
    except ValueError as error:
        raise TaskPackError(f"{label} escapes the project root") from error
    return candidate


def _is_link(path: Path) -> bool:
    is_junction = getattr(path, "is_junction", lambda: False)
    return path.is_symlink() or is_junction()


def _repository_snapshot(repository: Path) -> dict[str, Any]:
    if not repository.is_dir():
        raise TaskPackError(f"task repository does not exist: {repository}")
    if _is_link(repository):
        raise TaskPackError("task repositories may not be filesystem links")
    entries: list[dict[str, Any]] = []
    for path in sorted(
        repository.rglob("*"), key=lambda item: item.relative_to(repository).as_posix()
    ):
        relative = path.relative_to(repository).as_posix()
        if path.name == ".git" or "/.git/" in f"/{relative}/":
            raise TaskPackError("task repositories may not contain Git metadata")
        if _is_link(path):
            raise TaskPackError("task repositories may not contain filesystem links")
        if path.is_dir():
            entries.append({"path": relative, "type": "directory"})
        elif path.is_file():
            try:
                content = path.read_bytes()
            except OSError as error:
                raise TaskPackError(
                    f"could not read task repository entry: {relative}"
                ) from error
            entries.append(
                {
                    "path": relative,
                    "type": "file",
                    "bytes": len(content),
                    "sha256": hashlib.sha256(content).hexdigest(),
                }
            )
        else:
            raise TaskPackError(f"unsupported repository entry: {relative}")
    return {"fingerprint": _fingerprint(entries), "file_count": len(entries)}


def _validate_manifest(value: Mapping[str, Any]) -> None:
    if set(value) != PACK_FIELDS or value.get("version") != 1:
        raise TaskPackError("task pack must contain exactly the version 1 fields")
    for field in ("pack_id", "title", "experiment_ref"):
        if not isinstance(value.get(field), str) or not value[field]:
            raise TaskPackError(f"{field} must be a non-empty string")
    if not ID_PATTERN.fullmatch(value["pack_id"]):
        raise TaskPackError("pack_id must be a path-safe ID")
    requirements = value.get("requirements")
    if not isinstance(requirements, Mapping) or set(requirements) != REQUIREMENT_FIELDS:
        raise TaskPackError("task-pack requirements fields are invalid")
    for field in ("minimum_distinct_repositories", "minimum_seeds"):
        number = requirements.get(field)
        if isinstance(number, bool) or not isinstance(number, int) or number <= 0:
            raise TaskPackError(f"{field} must be a positive integer")
    if requirements["minimum_distinct_repositories"] < 2:
        raise TaskPackError("task packs require at least two distinct repositories")
    if requirements["minimum_seeds"] < 2:
        raise TaskPackError("task packs require repeated seeds")
    categories = requirements.get("required_categories")
    if (
        not isinstance(categories, list)
        or any(not isinstance(category, str) for category in categories)
        or set(categories) != REQUIRED_CATEGORIES
        or len(categories) != len(set(categories))
    ):
        raise TaskPackError("required categories must contain the representative task mix")
    bindings = value.get("task_bindings")
    if not isinstance(bindings, list) or not bindings:
        raise TaskPackError("task pack requires task bindings")
    identifiers: list[str] = []
    for binding in bindings:
        if not isinstance(binding, Mapping) or set(binding) != BINDING_FIELDS:
            raise TaskPackError("task binding fields are invalid")
        identifier = binding.get("id")
        if not isinstance(identifier, str) or not ID_PATTERN.fullmatch(identifier):
            raise TaskPackError("task binding ID must be path-safe")
        identifiers.append(identifier)
        if binding.get("category") not in REQUIRED_CATEGORIES:
            raise TaskPackError("task binding category is invalid")
        if binding.get("expected_baseline_outcome") != "fail":
            raise TaskPackError("representative tasks must declare a failing baseline")
        failing = binding.get("expected_failing_evaluator_ids")
        if (
            not isinstance(failing, list)
            or not failing
            or any(
                not isinstance(item, str) or not ID_PATTERN.fullmatch(item)
                for item in failing
            )
            or len(failing) != len(set(failing))
        ):
            raise TaskPackError("expected failing evaluator IDs must be unique strings")
    if len(identifiers) != len(set(identifiers)):
        raise TaskPackError("task binding IDs must be unique")


def validate_task_pack(project_root: Path, manifest_path: Path) -> dict[str, Any]:
    """Return a fingerprinted readiness report after offline checks pass."""

    project_root = project_root.resolve()
    if not project_root.is_dir():
        raise TaskPackError("project root does not exist")
    manifest_path = manifest_path.resolve()
    try:
        manifest_path.relative_to(project_root)
    except ValueError as error:
        raise TaskPackError("task-pack manifest must be inside the project root") from error
    manifest = _load_object(manifest_path, "task-pack manifest")
    _validate_manifest(manifest)
    plan = _load_object(
        _resolve_inside(project_root, manifest["experiment_ref"], "experiment reference"),
        "experiment plan",
    )
    try:
        validate_experiment_plan(plan)
    except ExperimentError as error:
        raise TaskPackError(f"experiment plan is invalid: {error}") from error

    requirements = manifest["requirements"]
    if len(plan["seeds"]) < requirements["minimum_seeds"]:
        raise TaskPackError("experiment does not meet the minimum repeated-seed count")
    tasks_by_id = {task["id"]: task for task in plan["tasks"]}
    bindings = {binding["id"]: binding for binding in manifest["task_bindings"]}
    if set(tasks_by_id) != set(bindings):
        raise TaskPackError("task bindings must exactly match experiment tasks")
    categories = {binding["category"] for binding in bindings.values()}
    if not set(requirements["required_categories"]).issubset(categories):
        raise TaskPackError("experiment does not contain every required task category")
    repositories = {
        _resolve_inside(project_root, task["repository"], "task repository reference")
        for task in tasks_by_id.values()
    }
    if len(repositories) < requirements["minimum_distinct_repositories"]:
        raise TaskPackError("experiment does not meet the distinct-repository minimum")

    arms = [plan["control"], *plan["treatments"]]
    task_reports: list[dict[str, Any]] = []
    for task_id in sorted(tasks_by_id):
        task = tasks_by_id[task_id]
        binding = bindings[task_id]
        repository = _resolve_inside(
            project_root, task["repository"], "task repository reference"
        )
        snapshot = _repository_snapshot(repository)
        for label, reference in (
            ("specification reference", task["spec_ref"]),
            ("evidence contract reference", binding["evidence_contract_ref"]),
        ):
            candidate = _resolve_inside(repository, reference, label)
            if not candidate.is_file():
                raise TaskPackError(f"{label} does not exist for task {task_id}")
        for arm in arms:
            workflow = _resolve_inside(repository, arm["config_ref"], "workflow reference")
            if not workflow.is_file():
                raise TaskPackError(f"workflow does not exist for task {task_id}")

        contract = _load_object(
            _resolve_inside(
                repository,
                binding["evidence_contract_ref"],
                "evidence contract reference",
            ),
            "evidence contract",
        )
        if contract.get("work_item_id") != task_id:
            raise TaskPackError("evidence-contract work item does not match task ID")
        for evaluator in contract.get("evaluators", []):
            if (
                isinstance(evaluator, Mapping)
                and evaluator.get("type") == "command"
                and evaluator.get("command", [])[:3] != SAFE_COMMAND_PREFIX
            ):
                raise TaskPackError(
                    "task-pack command evaluators must use standard-library unittest"
                )
        with tempfile.TemporaryDirectory(prefix="agentic-engineering-task-pack-") as temp:
            candidate = Path(temp) / "repository"
            try:
                shutil.copytree(repository, candidate)
                baseline = run_single_pass_baseline(contract, candidate)
            except (OSError, EvaluationError) as error:
                raise TaskPackError(
                    f"could not evaluate the baseline for task {task_id}: {error}"
                ) from error
        failing = sorted(
            result["evaluator_id"]
            for result in baseline["evaluator_results"]
            if result["outcome"] != "pass"
        )
        expected_failing = sorted(binding["expected_failing_evaluator_ids"])
        if baseline["outcome"] != binding["expected_baseline_outcome"]:
            raise TaskPackError(f"baseline outcome changed for task {task_id}")
        if failing != expected_failing:
            raise TaskPackError(f"failing baseline evaluators changed for task {task_id}")
        if baseline["regressions"]:
            raise TaskPackError(f"initial task baseline has protected regressions: {task_id}")
        task_reports.append(
            {
                "id": task_id,
                "category": binding["category"],
                "repository": task["repository"],
                "repository_fingerprint": snapshot["fingerprint"],
                "repository_entry_count": snapshot["file_count"],
                "baseline_outcome": baseline["outcome"],
                "failing_evaluator_ids": failing,
                "protected_regressions": baseline["regressions"],
            }
        )

    payload = {
        "version": 1,
        "pack_id": manifest["pack_id"],
        "status": "ready",
        "experiment_ref": manifest["experiment_ref"],
        "experiment_id": plan["experiment_id"],
        "plan_fingerprint": experiment_plan_fingerprint(plan),
        "pack_fingerprint": _fingerprint(manifest),
        "distinct_repository_count": len(repositories),
        "categories": sorted(categories),
        "task_count": len(plan["tasks"]),
        "seed_count": len(plan["seeds"]),
        "arm_count": len(arms),
        "matrix_size": len(experiment_cells(plan)),
        "model_calls_performed": False,
        "tasks": task_reports,
    }
    fingerprint = _fingerprint(payload)
    return {
        **payload,
        "report_id": f"task-pack-readiness-{fingerprint[:16]}",
        "fingerprint": fingerprint,
    }


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest", type=Path)
    parser.add_argument("--project-root", type=Path, default=Path.cwd())
    parser.add_argument("--output", "-o", type=Path)
    arguments = parser.parse_args(argv)
    report = validate_task_pack(arguments.project_root, arguments.manifest)
    output = json.dumps(report, ensure_ascii=False, indent=2) + "\n"
    if arguments.output:
        arguments.output.write_text(output, encoding="utf-8")
    else:
        sys.stdout.write(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
