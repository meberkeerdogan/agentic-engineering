"""Deterministic static and adaptive dependency-plan experiments."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any


class DependencyPlanError(ValueError):
    """Raised when a dependency plan is inconsistent or cyclic."""


ID_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")


def _canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"), sort_keys=True)


def _fingerprint(value: Any) -> str:
    return hashlib.sha256(_canonical_json(value).encode("utf-8")).hexdigest()


def _evidence_refs(value: Any) -> bool:
    return (
        isinstance(value, list)
        and bool(value)
        and all(isinstance(item, str) and item for item in value)
        and len(value) == len(set(value))
    )


def _validate(
    manifest: Mapping[str, Any],
) -> tuple[list[str], dict[str, list[str]], dict[str, int], dict[str, str]]:
    if manifest.get("version") != 1 or not isinstance(manifest.get("plan_id"), str):
        raise DependencyPlanError("dependency plan must use version 1 and a plan ID")
    if not ID_PATTERN.fullmatch(manifest["plan_id"]):
        raise DependencyPlanError("plan ID must be path-safe")
    tasks = manifest.get("tasks")
    states = manifest.get("runtime_states")
    if not isinstance(tasks, list) or not tasks or not isinstance(states, list):
        raise DependencyPlanError("tasks and runtime states must be arrays")
    order: list[str] = []
    dependencies: dict[str, list[str]] = {}
    priorities: dict[str, int] = {}
    for task in tasks:
        if (
            not isinstance(task, Mapping)
            or not isinstance(task.get("id"), str)
            or not ID_PATTERN.fullmatch(task["id"])
        ):
            raise DependencyPlanError("tasks require string IDs")
        task_id = task["id"]
        depends_on = task.get("depends_on")
        priority = task.get("priority")
        if task_id in dependencies or not isinstance(depends_on, list):
            raise DependencyPlanError("task IDs must be unique and dependencies must be arrays")
        if any(not isinstance(item, str) for item in depends_on) or len(depends_on) != len(set(depends_on)):
            raise DependencyPlanError("dependencies must be unique task IDs")
        if isinstance(priority, bool) or not isinstance(priority, int):
            raise DependencyPlanError("task priority must be an integer")
        if not _evidence_refs(task.get("evidence_refs")):
            raise DependencyPlanError("tasks require unique evidence references")
        order.append(task_id)
        dependencies[task_id] = list(depends_on)
        priorities[task_id] = priority
    known = set(order)
    if any(dependency not in known for values in dependencies.values() for dependency in values):
        raise DependencyPlanError("dependencies must reference declared tasks")
    state_by_id = {task_id: "pending" for task_id in order}
    seen_states: set[str] = set()
    for state in states:
        if not isinstance(state, Mapping) or state.get("id") not in known:
            raise DependencyPlanError("runtime states must reference declared tasks")
        task_id = state["id"]
        value = state.get("state")
        if task_id in seen_states or value not in {"pending", "completed", "failed"}:
            raise DependencyPlanError("runtime states must be unique and supported")
        if not _evidence_refs(state.get("evidence_refs")):
            raise DependencyPlanError("runtime states require unique evidence references")
        seen_states.add(task_id)
        state_by_id[task_id] = value
    _topological_order(order, dependencies, priorities, adaptive=False)
    return order, dependencies, priorities, state_by_id


def _topological_order(
    declared: list[str],
    dependencies: dict[str, list[str]],
    priorities: dict[str, int],
    *,
    adaptive: bool,
) -> list[str]:
    remaining = set(declared)
    result: list[str] = []
    index = {task_id: position for position, task_id in enumerate(declared)}
    while remaining:
        ready = [task_id for task_id in remaining if set(dependencies[task_id]) <= set(result)]
        if not ready:
            raise DependencyPlanError("dependency plan contains a cycle")
        if adaptive:
            ready.sort(key=lambda task_id: (-priorities[task_id], task_id))
        else:
            ready.sort(key=index.__getitem__)
        selected = ready[0]
        result.append(selected)
        remaining.remove(selected)
    return result


def build_dependency_plan(manifest: Mapping[str, Any], strategy: str) -> dict[str, Any]:
    """Build a read-only plan view for the selected experimental strategy."""

    if strategy not in {"static", "adaptive"}:
        raise DependencyPlanError("strategy must be static or adaptive")
    declared, dependencies, priorities, states = _validate(manifest)
    completed = {task_id for task_id, state in states.items() if state == "completed"}
    failed = {task_id for task_id, state in states.items() if state == "failed"}
    blocked = set(failed)
    changed = True
    while changed:
        changed = False
        for task_id, task_dependencies in dependencies.items():
            if task_id not in blocked and set(task_dependencies) & blocked:
                blocked.add(task_id)
                changed = True
    pending = set(declared) - completed - failed
    ready = {
        task_id
        for task_id in pending
        if set(dependencies[task_id]) <= completed and task_id not in blocked
    }
    static_order = _topological_order(declared, dependencies, priorities, adaptive=False)
    if strategy == "static":
        ordered = [task_id for task_id in static_order if task_id not in completed | failed]
    else:
        adaptive_order = _topological_order(declared, dependencies, priorities, adaptive=True)
        ordered = [task_id for task_id in adaptive_order if task_id in pending - blocked]
    decisions = []
    for task_id in declared:
        if task_id in completed:
            disposition, reason = "completed", "runtime evidence marks the task completed"
        elif task_id in failed:
            disposition, reason = "failed", "runtime evidence marks the task failed"
        elif task_id in blocked:
            disposition, reason = "blocked", "a transitive dependency failed"
        elif task_id in ready:
            disposition, reason = "ready", "all dependencies have completion evidence"
        else:
            disposition, reason = "waiting", "at least one dependency is incomplete"
        decisions.append({"task_id": task_id, "disposition": disposition, "reason": reason})
    report: dict[str, Any] = {
        "version": 1,
        "plan_id": manifest["plan_id"],
        "strategy": strategy,
        "source_fingerprint": _fingerprint(manifest),
        "ordered_task_ids": ordered,
        "ready_task_ids": sorted(ready, key=lambda task_id: (-priorities[task_id], task_id)),
        "blocked_task_ids": sorted(blocked - failed),
        "completed_task_ids": sorted(completed),
        "failed_task_ids": sorted(failed),
        "decisions": decisions,
        "executions": [],
        "state_mutations": [],
    }
    fingerprint = _fingerprint(report)
    report["report_id"] = f"dependency-plan-{fingerprint[:16]}"
    report["fingerprint"] = fingerprint
    return report


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest", type=Path)
    parser.add_argument("--strategy", choices=("static", "adaptive"), required=True)
    parser.add_argument("--output", type=Path, required=True)
    arguments = parser.parse_args(argv)
    manifest = json.loads(arguments.manifest.read_text("utf-8"))
    report = build_dependency_plan(manifest, arguments.strategy)
    arguments.output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
