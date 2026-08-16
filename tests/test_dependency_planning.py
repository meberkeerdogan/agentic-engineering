import json
from pathlib import Path

import pytest

from agentic_engineering.dependency_planning import (
    DependencyPlanError,
    build_dependency_plan,
)


ROOT = Path(__file__).resolve().parents[1]


def manifest() -> dict:
    return json.loads((ROOT / "examples/dependency-plan.json").read_text("utf-8"))


def test_static_plan_preserves_declared_topological_work() -> None:
    report = build_dependency_plan(manifest(), "static")
    expected = ROOT / "examples" / "expected-static-dependency-plan.json"
    assert report == json.loads(expected.read_text("utf-8"))
    assert report["ordered_task_ids"] == ["docs", "integration", "release"]
    assert report["ready_task_ids"] == ["docs"]
    assert report["blocked_task_ids"] == ["integration", "release"]
    assert report["executions"] == []
    assert report["state_mutations"] == []


def test_adaptive_plan_removes_failure_dependent_work() -> None:
    first = build_dependency_plan(manifest(), "adaptive")
    second = build_dependency_plan(manifest(), "adaptive")
    assert first == second
    expected = ROOT / "examples" / "expected-adaptive-dependency-plan.json"
    assert first == json.loads(expected.read_text("utf-8"))
    assert first["ordered_task_ids"] == ["docs"]
    assert first["ready_task_ids"] == ["docs"]
    assert first["blocked_task_ids"] == ["integration", "release"]


def test_cycle_and_unknown_dependency_fail_closed() -> None:
    value = manifest()
    value["tasks"][0]["depends_on"] = ["release"]
    with pytest.raises(DependencyPlanError, match="cycle"):
        build_dependency_plan(value, "adaptive")
    value = manifest()
    value["tasks"][0]["depends_on"] = ["missing"]
    with pytest.raises(DependencyPlanError, match="declared"):
        build_dependency_plan(value, "static")


def test_runtime_states_cannot_be_duplicated() -> None:
    value = manifest()
    value["runtime_states"].append(value["runtime_states"][0])
    with pytest.raises(DependencyPlanError, match="unique"):
        build_dependency_plan(value, "adaptive")
