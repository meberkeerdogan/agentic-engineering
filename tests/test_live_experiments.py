import json
import shutil
import sys
from datetime import date
from pathlib import Path

import pytest

import agentic_engineering.live_experiments as live_module
from agentic_engineering.batch_experiments import BatchExperimentError
from agentic_engineering.codex_adapter import CodexAdapterError
from agentic_engineering.codex_environment import CodexEnvironmentError
from agentic_engineering.live_experiments import (
    LiveExperimentError,
    main,
    run_live_experiment,
)
from agentic_engineering.watchdog import analyze_trajectory


ROOT = Path(__file__).resolve().parents[1]
FAKE_CODEX = ROOT / "tests" / "fixtures" / "fake_live_codex.py"


def project_fixture(tmp_path: Path) -> Path:
    project = tmp_path / "project"
    (project / "examples").mkdir(parents=True)
    shutil.copytree(
        ROOT / "examples" / "live-pilot-template",
        project / "examples" / "live-pilot-template",
    )
    for name in (
        "live-experiment.json",
        "live-batch-experiment.json",
        "live-experiment-record.json",
        "live-pilot-rates.json",
        "codex-environment.json",
    ):
        shutil.copy(ROOT / "examples" / name, project / "examples")
    fake_home = project / ".fake-codex-home"
    (fake_home / "tmp").mkdir(parents=True)
    (fake_home / "auth.json").write_text("{}\n", encoding="utf-8")
    return project


def run_offline(project: Path):
    return run_live_experiment(
        project,
        project / "examples" / "live-experiment.json",
        command_prefix=(sys.executable, str(FAKE_CODEX)),
        source_codex_home=project / ".fake-codex-home",
        preflight_date=date(2026, 8, 16),
    )


def batch_dir(project: Path) -> Path:
    return project / ".agentic-runs" / "live-batches" / "codex-workflow-comparison-003"


def representative_project_fixture(tmp_path: Path) -> Path:
    project = project_fixture(tmp_path)
    shutil.copytree(ROOT / "examples" / "task-pack", project / "examples" / "task-pack")
    for name in (
        "representative-sentinel-experiment.json",
        "representative-sentinel-batch.json",
        "representative-sentinel-live.json",
        "evolution-sentinel-experiment.json",
        "evolution-sentinel-batch.json",
        "evolution-sentinel-live.json",
        "dependency-planning-sentinel-experiment.json",
        "dependency-planning-sentinel-batch.json",
        "dependency-planning-sentinel-live.json",
    ):
        shutil.copy(ROOT / "examples" / name, project / "examples")
    return project


def run_representative_offline(project: Path):
    return run_live_experiment(
        project,
        project / "examples" / "representative-sentinel-live.json",
        command_prefix=(sys.executable, str(FAKE_CODEX)),
        source_codex_home=project / ".fake-codex-home",
        preflight_date=date(2026, 8, 16),
    )


def run_evolution_offline(project: Path):
    return run_live_experiment(
        project,
        project / "examples" / "evolution-sentinel-live.json",
        command_prefix=(sys.executable, str(FAKE_CODEX)),
        source_codex_home=project / ".fake-codex-home",
        preflight_date=date(2026, 8, 16),
    )


def run_dependency_planning_offline(project: Path):
    return run_live_experiment(
        project,
        project / "examples" / "dependency-planning-sentinel-live.json",
        command_prefix=(sys.executable, str(FAKE_CODEX)),
        source_codex_home=project / ".fake-codex-home",
        preflight_date=date(2026, 8, 16),
    )


def test_live_experiment_pauses_then_resumes_with_fresh_preflight_per_cell(
    tmp_path: Path,
) -> None:
    project = project_fixture(tmp_path)

    first = run_offline(project)
    second = run_offline(project)

    root = batch_dir(project)
    assert first.status == "paused"
    assert first.completed_count == 1
    assert second.status == "completed"
    assert second.completed_count == second.matrix_size == 2
    assert len(list((root / "live-workspaces").iterdir())) == 2
    assert len(list((root / "live-preflight").glob("*.json"))) == 2
    assert len(list((root / "live-status").glob("*.json"))) == 2
    assert len(list((root / "live-evidence").glob("*/trajectory.json"))) == 2
    assert len(list((root / "live-evidence").glob("*/trajectory-source.json"))) == 2
    assert not list((project / ".fake-codex-home" / "tmp").iterdir())
    state = json.loads((root / "batch-state.json").read_text("utf-8"))
    assert len(state["execution_fingerprint"]) == 64
    assert all(cell["status"] == "completed" for cell in state["cells"])
    assert all(
        any(ref.startswith("live-preflight/") for ref in cell["observation"]["evidence_refs"])
        for cell in state["cells"]
    )
    assert all(
        any(ref.endswith("/trajectory.json") for ref in cell["observation"]["evidence_refs"])
        and any(
            ref.endswith("/trajectory-source.json")
            for ref in cell["observation"]["evidence_refs"]
        )
        for cell in state["cells"]
    )
    for path in (root / "live-evidence").glob("*/trajectory.json"):
        trajectory = json.loads(path.read_text("utf-8"))
        assert [event["phase"] for event in trajectory["events"]] == [
            "reproduce",
            "patch",
            "validate",
            "complete",
            "validate",
        ]
        assert analyze_trajectory(trajectory)["signal_count"] == 0
    for path in (root / "live-evidence").glob("*/trajectory-source.json"):
        source = path.read_text("utf-8")
        assert "python -m unittest" not in source
        assert "simulated initial failure" not in source
    workspaces = list((root / "live-workspaces").iterdir())
    control_workspace = next(
        workspace for workspace in workspaces if (workspace / "workflow-control.md").is_file()
    )
    treatment_workspace = next(
        workspace
        for workspace in workspaces
        if (workspace / "workflow-treatment.md").is_file()
    )
    assert (control_workspace / "workflow-control.md").is_file()
    assert not (control_workspace / "workflow-treatment.md").exists()
    assert (treatment_workspace / "workflow-treatment.md").is_file()
    assert not (treatment_workspace / "workflow-control.md").exists()
    report = json.loads(second.report_path.read_text("utf-8"))
    assert report["run_count"] == 2
    assert {run["arm_id"] for run in report["runs"]} == {
        "control-bounded",
        "treatment-verified-loop",
    }


def test_representative_sentinel_is_bounded_and_resumable_offline(
    tmp_path: Path,
) -> None:
    project = representative_project_fixture(tmp_path)

    first = run_representative_offline(project)
    second = run_representative_offline(project)

    root = (
        project
        / ".agentic-runs"
        / "live-batches"
        / "codex-representative-sentinel-001"
    )
    assert first.status == "paused"
    assert first.completed_count == 1
    assert second.status == "completed"
    assert second.completed_count == second.matrix_size == 2
    state = json.loads((root / "batch-state.json").read_text("utf-8"))
    assert state["spent_cost"] <= 1
    assert all(cell["observation"]["cost"] <= 0.5 for cell in state["cells"])
    assert all(cell["observation"]["verified_complete"] for cell in state["cells"])
    assert all(cell["observation"]["regressions"] == 0 for cell in state["cells"])
    assert len(list((root / "live-evidence").glob("*/trajectory.json"))) == 2


def test_evolution_sentinel_is_bounded_and_resumable_offline(tmp_path: Path) -> None:
    project = representative_project_fixture(tmp_path)

    first = run_evolution_offline(project)
    second = run_evolution_offline(project)

    root = project / ".agentic-runs" / "live-batches" / "codex-evolution-sentinel-001"
    assert first.status == "paused"
    assert first.completed_count == 1
    assert second.status == "completed"
    assert second.completed_count == second.matrix_size == 2
    state = json.loads((root / "batch-state.json").read_text("utf-8"))
    assert state["spent_cost"] <= 1.5
    assert all(cell["observation"]["cost"] <= 0.75 for cell in state["cells"])
    assert all(cell["observation"]["verified_complete"] for cell in state["cells"])
    assert all(cell["observation"]["regressions"] == 0 for cell in state["cells"])
    assert len(list((root / "live-evidence").glob("*/trajectory.json"))) == 2


def test_dependency_planning_sentinel_is_bounded_and_isolates_policy(
    tmp_path: Path,
) -> None:
    project = representative_project_fixture(tmp_path)

    first = run_dependency_planning_offline(project)
    second = run_dependency_planning_offline(project)

    root = (
        project
        / ".agentic-runs"
        / "live-batches"
        / "codex-planning-sentinel-001"
    )
    assert first.status == "paused"
    assert first.completed_count == 1
    assert second.status == "completed"
    assert second.completed_count == second.matrix_size == 2
    state = json.loads((root / "batch-state.json").read_text("utf-8"))
    assert state["spent_cost"] <= 1.5
    assert all(cell["observation"]["cost"] <= 0.75 for cell in state["cells"])
    assert all(cell["observation"]["verified_complete"] for cell in state["cells"])
    assert all(cell["observation"]["regressions"] == 0 for cell in state["cells"])
    assert all(cell["observation"]["human_interventions"] == 0 for cell in state["cells"])
    workspaces = list((root / "live-workspaces").iterdir())
    static_workspace = next(
        workspace
        for workspace in workspaces
        if (workspace / "workflow-static-plan.md").is_file()
    )
    adaptive_workspace = next(
        workspace
        for workspace in workspaces
        if (workspace / "workflow-adaptive-plan.md").is_file()
    )
    assert not (static_workspace / "workflow-adaptive-plan.md").exists()
    assert not (adaptive_workspace / "workflow-static-plan.md").exists()
    report = json.loads(second.report_path.read_text("utf-8"))
    assert {run["arm_id"] for run in report["runs"]} == {
        "control-static",
        "treatment-adaptive",
    }


def test_completed_live_experiment_does_not_execute_cells_again(tmp_path: Path) -> None:
    project = project_fixture(tmp_path)
    run_offline(project)
    completed = run_offline(project)

    again = run_offline(project)

    assert again.status == "completed"
    assert again.spent_cost == completed.spent_cost
    assert len(list((batch_dir(project) / "live-workspaces").iterdir())) == 2


def test_changed_template_cannot_be_mixed_into_resumed_batch(tmp_path: Path) -> None:
    project = project_fixture(tmp_path)
    run_offline(project)
    treatment = project / "examples" / "live-pilot-template" / "workflow-treatment.md"
    treatment.write_text(treatment.read_text("utf-8") + "\nChanged.\n", encoding="utf-8")

    with pytest.raises(BatchExperimentError, match="execution inputs changed"):
        run_offline(project)

    assert len(list((batch_dir(project) / "live-workspaces").iterdir())) == 1


def test_copy_must_match_the_bound_template_snapshot(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    project = project_fixture(tmp_path)
    real_copytree = live_module.shutil.copytree

    def changing_copytree(source, destination):
        result = real_copytree(source, destination)
        (Path(destination) / "calculator.py").write_text("changed during copy\n", encoding="utf-8")
        return result

    monkeypatch.setattr(live_module.shutil, "copytree", changing_copytree)

    with pytest.raises(LiveExperimentError, match="does not match the bound template"):
        run_offline(project)

    assert not (batch_dir(project) / "live-evidence").exists()


def test_changed_rate_card_cannot_be_mixed_into_resumed_batch(tmp_path: Path) -> None:
    project = project_fixture(tmp_path)
    run_offline(project)
    path = project / "examples" / "live-pilot-rates.json"
    rates = json.loads(path.read_text("utf-8"))
    rates["output_per_million"] = 31
    path.write_text(json.dumps(rates), encoding="utf-8")

    with pytest.raises(BatchExperimentError, match="execution inputs changed"):
        run_offline(project)


def test_changed_codex_version_cannot_be_mixed_into_resumed_batch(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    project = project_fixture(tmp_path)
    run_offline(project)
    monkeypatch.setenv("FAKE_CODEX_VERSION", "0.148.0")

    with pytest.raises(BatchExperimentError, match="execution inputs changed"):
        run_offline(project)


def test_changed_capture_version_cannot_be_mixed_into_resumed_batch(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    project = project_fixture(tmp_path)
    run_offline(project)
    monkeypatch.setattr(live_module, "TRAJECTORY_CAPTURE_VERSION", 2)

    with pytest.raises(BatchExperimentError, match="execution inputs changed"):
        run_offline(project)


def test_preflight_failure_blocks_model_execution_and_persists_only_type(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    project = project_fixture(tmp_path)
    monkeypatch.setenv("FAKE_CODEX_MODEL", "different-model")

    with pytest.raises(CodexEnvironmentError, match="absent from the Codex catalog"):
        run_offline(project)

    root = batch_dir(project)
    assert not (root / "live-evidence").exists()
    status = json.loads(next((root / "live-status").glob("*.json")).read_text("utf-8"))
    assert status == {
        "version": 1,
        "cell_id": "a-control-bounded__t-median-fix__s-0",
        "status": "failed",
        "error_type": "CodexEnvironmentError",
    }
    state_text = (root / "batch-state.json").read_text("utf-8")
    assert "absent from the Codex catalog" not in state_text


def test_missing_auto_review_support_blocks_batch_before_model_execution(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    project = project_fixture(tmp_path)
    monkeypatch.setenv("FAKE_CODEX_AUTO_REVIEW", "missing")

    with pytest.raises(CodexAdapterError, match="does not support --approve-for-me"):
        run_offline(project)

    assert not batch_dir(project).exists()


def test_live_timeout_must_fit_inside_batch_ceiling(tmp_path: Path) -> None:
    project = project_fixture(tmp_path)
    path = project / "examples" / "live-experiment.json"
    value = json.loads(path.read_text("utf-8"))
    value["timeout_seconds"] = 601
    path.write_text(json.dumps(value), encoding="utf-8")

    with pytest.raises(LiveExperimentError, match="exceeds the batch per-run"):
        run_offline(project)

    assert not batch_dir(project).exists()


def test_task_bindings_must_exactly_match_planned_tasks(tmp_path: Path) -> None:
    project = project_fixture(tmp_path)
    path = project / "examples" / "live-experiment.json"
    value = json.loads(path.read_text("utf-8"))
    value["task_bindings"][0]["id"] = "other-task"
    path.write_text(json.dumps(value), encoding="utf-8")

    with pytest.raises(LiveExperimentError, match="exactly match experiment tasks"):
        run_offline(project)


def test_control_and_treatment_require_distinct_workflow_files(tmp_path: Path) -> None:
    project = project_fixture(tmp_path)
    path = project / "examples" / "live-experiment-record.json"
    value = json.loads(path.read_text("utf-8"))
    value["treatments"][0]["config_ref"] = value["control"]["config_ref"]
    path.write_text(json.dumps(value), encoding="utf-8")

    with pytest.raises(LiveExperimentError, match="distinct workflow configs"):
        run_offline(project)

    assert not batch_dir(project).exists()


def test_rate_unit_must_match_declared_batch_metric(tmp_path: Path) -> None:
    project = project_fixture(tmp_path)
    path = project / "examples" / "live-pilot-rates.json"
    value = json.loads(path.read_text("utf-8"))
    value["unit"] = "USD"
    path.write_text(json.dumps(value), encoding="utf-8")

    with pytest.raises(LiveExperimentError, match="batch cost unit"):
        run_offline(project)

    assert not batch_dir(project).exists()


def test_live_config_rejects_undeclared_fields(tmp_path: Path) -> None:
    project = project_fixture(tmp_path)
    path = project / "examples" / "live-experiment.json"
    value = json.loads(path.read_text("utf-8"))
    value["surprise"] = True
    path.write_text(json.dumps(value), encoding="utf-8")

    with pytest.raises(LiveExperimentError, match="exactly the version 1 fields"):
        run_offline(project)


def test_template_git_metadata_is_rejected_before_batch_creation(tmp_path: Path) -> None:
    project = project_fixture(tmp_path)
    (project / "examples" / "live-pilot-template" / ".git").mkdir()

    with pytest.raises(LiveExperimentError, match="Git metadata"):
        run_offline(project)

    assert not batch_dir(project).exists()


def test_cli_requires_explicit_paid_run_confirmation(tmp_path: Path) -> None:
    project = project_fixture(tmp_path)

    with pytest.raises(LiveExperimentError, match="--confirm-paid-run"):
        main(
            [
                str(project / "examples" / "live-experiment.json"),
                "--project-root",
                str(project),
            ]
        )

    assert not batch_dir(project).exists()


def test_live_config_must_be_inside_project_root(tmp_path: Path) -> None:
    project = project_fixture(tmp_path)
    outside = tmp_path / "outside.json"
    outside.write_text("{}", encoding="utf-8")

    with pytest.raises(LiveExperimentError, match="inside the project root"):
        run_live_experiment(project, outside)
