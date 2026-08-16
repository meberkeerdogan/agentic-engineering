import json
import shutil
from pathlib import Path

import pytest

from agentic_engineering.evaluators import run_single_pass_baseline
from agentic_engineering.task_pack import TaskPackError, main, validate_task_pack


ROOT = Path(__file__).resolve().parents[1]


def project_fixture(tmp_path: Path) -> Path:
    project = tmp_path / "project"
    examples = project / "examples"
    examples.mkdir(parents=True)
    shutil.copytree(
        ROOT / "examples" / "live-pilot-template",
        examples / "live-pilot-template",
    )
    shutil.copytree(ROOT / "examples" / "task-pack", examples / "task-pack")
    for name in ("evaluation-task-pack.json", "evaluation-task-pack-experiment.json"):
        shutil.copy(ROOT / "examples" / name, examples)
    return project


def test_representative_task_pack_is_ready_without_model_calls() -> None:
    manifest = ROOT / "examples" / "evaluation-task-pack.json"

    first = validate_task_pack(ROOT, manifest)
    second = validate_task_pack(ROOT, manifest)
    expected = json.loads(
        (ROOT / "examples" / "expected-task-pack-readiness.json").read_text("utf-8")
    )

    assert first == second == expected
    assert first["status"] == "ready"
    assert first["distinct_repository_count"] == 3
    assert first["task_count"] == 3
    assert first["seed_count"] == 3
    assert first["arm_count"] == 2
    assert first["matrix_size"] == 18
    assert first["model_calls_performed"] is False
    assert {task["category"] for task in first["tasks"]} == {
        "bounded-bug-fix",
        "multi-file-feature",
        "multi-step-evolution",
    }
    assert all(task["baseline_outcome"] == "fail" for task in first["tasks"])
    assert all(not task["protected_regressions"] for task in first["tasks"])
    assert not list((ROOT / "examples" / "task-pack").rglob("__pycache__"))


def test_cli_writes_fingerprinted_readiness_report(tmp_path: Path) -> None:
    output = tmp_path / "readiness.json"

    result = main(
        [
            str(ROOT / "examples" / "evaluation-task-pack.json"),
            "--project-root",
            str(ROOT),
            "--output",
            str(output),
        ]
    )

    report = json.loads(output.read_text("utf-8"))
    assert result == 0
    assert report["report_id"].startswith("task-pack-readiness-")
    assert len(report["fingerprint"]) == 64


def test_changed_baseline_fails_closed(tmp_path: Path) -> None:
    project = project_fixture(tmp_path)
    path = project / "examples" / "evaluation-task-pack.json"
    manifest = json.loads(path.read_text("utf-8"))
    manifest["task_bindings"][1]["expected_failing_evaluator_ids"] = ["other"]
    path.write_text(json.dumps(manifest), encoding="utf-8")

    with pytest.raises(TaskPackError, match="failing baseline evaluators changed"):
        validate_task_pack(project, path)


def test_repeated_seed_minimum_is_enforced(tmp_path: Path) -> None:
    project = project_fixture(tmp_path)
    path = project / "examples" / "evaluation-task-pack-experiment.json"
    plan = json.loads(path.read_text("utf-8"))
    plan["seeds"] = [0]
    path.write_text(json.dumps(plan), encoding="utf-8")

    with pytest.raises(TaskPackError, match="minimum repeated-seed count"):
        validate_task_pack(
            project, project / "examples" / "evaluation-task-pack.json"
        )


def test_every_arm_requires_a_workflow_in_every_repository(tmp_path: Path) -> None:
    project = project_fixture(tmp_path)
    workflow = (
        project
        / "examples"
        / "task-pack"
        / "multi-step-evolution"
        / "workflow-treatment.md"
    )
    workflow.unlink()

    with pytest.raises(TaskPackError, match="workflow does not exist"):
        validate_task_pack(
            project, project / "examples" / "evaluation-task-pack.json"
        )


def test_baseline_commands_cannot_invoke_arbitrary_tools(tmp_path: Path) -> None:
    project = project_fixture(tmp_path)
    contract_path = (
        project
        / "examples"
        / "task-pack"
        / "multi-file-feature"
        / "evidence-contract.json"
    )
    contract = json.loads(contract_path.read_text("utf-8"))
    contract["evaluators"][0]["command"] = ["external-agent", "run"]
    contract_path.write_text(json.dumps(contract), encoding="utf-8")

    with pytest.raises(TaskPackError, match="standard-library unittest"):
        validate_task_pack(
            project, project / "examples" / "evaluation-task-pack.json"
        )


def test_experiment_reference_cannot_escape_project(tmp_path: Path) -> None:
    project = project_fixture(tmp_path)
    manifest_path = project / "examples" / "evaluation-task-pack.json"
    manifest = json.loads(manifest_path.read_text("utf-8"))
    manifest["experiment_ref"] = "../../outside.json"
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")

    with pytest.raises(TaskPackError, match="escapes the project root"):
        validate_task_pack(project, manifest_path)


def test_new_representative_tasks_have_known_passing_solutions(tmp_path: Path) -> None:
    feature = tmp_path / "feature"
    evolution = tmp_path / "evolution"
    shutil.copytree(ROOT / "examples" / "task-pack" / "multi-file-feature", feature)
    shutil.copytree(ROOT / "examples" / "task-pack" / "multi-step-evolution", evolution)

    with (feature / "inventory.py").open("a", encoding="utf-8") as stream:
        stream.write(
            "\n\ndef low_stock_skus(items: list[dict], threshold: int = 5) -> list[str]:\n"
            "    if threshold < 0:\n"
            "        raise ValueError('threshold must be non-negative')\n"
            "    return sorted(normalize_sku(item['sku']) for item in items "
            "if item['quantity'] <= threshold)\n"
        )
    with (feature / "reporting.py").open("a", encoding="utf-8") as stream:
        stream.write(
            "\n\ndef format_restock_report(items: list[dict], threshold: int = 5) -> str:\n"
            "    from inventory import low_stock_skus\n"
            "    skus = low_stock_skus(items, threshold)\n"
            "    return 'Restock: ' + (', '.join(skus) if skus else 'none')\n"
        )

    with (evolution / "roadmap.py").open("a", encoding="utf-8") as stream:
        stream.write(
            "\n\ndef ready_item_ids(items: list[dict]) -> list[str]:\n"
            "    completed = set(completed_item_ids(items))\n"
            "    return sorted(item['id'] for item in items if item['status'] == "
            "'pending' and set(item['depends_on']) <= completed)\n"
            "\n\ndef blocking_dependencies(items: list[dict]) -> dict[str, list[str]]:\n"
            "    completed = set(completed_item_ids(items))\n"
            "    return {item['id']: sorted(set(item['depends_on']) - completed) "
            "for item in items if item['status'] == 'pending' and "
            "set(item['depends_on']) - completed}\n"
        )
    with (evolution / "progress.py").open("a", encoding="utf-8") as stream:
        stream.write(
            "\n\ndef build_progress_summary(items: list[dict]) -> dict:\n"
            "    from roadmap import blocking_dependencies, ready_item_ids\n"
            "    total = len(items)\n"
            "    completed = completed_count(items)\n"
            "    return {'total': total, 'completed': completed, "
            "'completion_ratio': round(completed / total, 2) if total else 0.0, "
            "'ready': ready_item_ids(items), "
            "'blocked': blocking_dependencies(items)}\n"
        )

    for repository in (feature, evolution):
        contract = json.loads((repository / "evidence-contract.json").read_text("utf-8"))
        report = run_single_pass_baseline(contract, repository)
        assert report["outcome"] == "pass"
        assert report["regressions"] == []
