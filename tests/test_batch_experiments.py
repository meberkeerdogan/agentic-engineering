import json
from copy import deepcopy
from pathlib import Path

import pytest
from test_core_schemas import load_json

from agentic_engineering.batch_experiments import (
    BatchExperimentConfig,
    BatchExperimentError,
    main,
    run_experiment_batch,
)
from agentic_engineering.experiments import RunObservation, replay_adapters

ROOT = Path(__file__).resolve().parents[1]


def plan() -> dict:
    return load_json("examples/experiment-record.json")


def replay() -> dict:
    return load_json("examples/experiment-observations.json")


def config_mapping() -> dict:
    return load_json("examples/batch-experiment.json")


def config(value: dict | None = None) -> BatchExperimentConfig:
    return BatchExperimentConfig.from_mapping(value or config_mapping())


class RecordingAdapter:
    def __init__(self, delegate, calls: list[tuple[str, str, int]]):
        self.delegate = delegate
        self.calls = calls

    def run(self, arm, task, seed):
        self.calls.append((arm["id"], task["id"], seed))
        return self.delegate.run(arm, task, seed)


def recording_adapters(calls: list[tuple[str, str, int]]) -> dict:
    selected_plan = plan()
    delegates = replay_adapters(selected_plan, replay())
    return {
        arm_id: RecordingAdapter(delegate, calls)
        for arm_id, delegate in delegates.items()
    }


def test_batch_pauses_and_resumes_without_repeating_completed_cells(tmp_path: Path) -> None:
    calls: list[tuple[str, str, int]] = []
    adapters = recording_adapters(calls)

    first = run_experiment_batch(plan(), adapters, config(), tmp_path)
    paused_state = json.loads(first.state_path.read_text("utf-8"))
    second = run_experiment_batch(plan(), adapters, config(), tmp_path)

    assert first.status == "paused"
    assert first.completed_count == 2
    assert first.report_path is None
    assert paused_state == load_json("examples/expected-batch-state.json")
    assert second.status == "completed"
    assert second.completed_count == 4
    assert len(calls) == 4
    assert len(calls) == len(set(calls))
    report = json.loads(second.report_path.read_text("utf-8"))
    assert report == load_json("examples/expected-experiment-report.json")


def test_completed_batch_is_idempotent(tmp_path: Path) -> None:
    calls: list[tuple[str, str, int]] = []
    adapters = recording_adapters(calls)
    run_experiment_batch(plan(), adapters, config(), tmp_path)
    completed = run_experiment_batch(plan(), adapters, config(), tmp_path)

    again = run_experiment_batch(plan(), adapters, config(), tmp_path)

    assert completed.status == again.status == "completed"
    assert len(calls) == 4


def test_changed_config_cannot_resume_existing_state(tmp_path: Path) -> None:
    run_experiment_batch(plan(), recording_adapters([]), config(), tmp_path)
    changed = config_mapping()
    changed["maximum_runs_per_invocation"] = 1

    with pytest.raises(BatchExperimentError, match="config changed"):
        run_experiment_batch(plan(), recording_adapters([]), config(changed), tmp_path)


def test_changed_plan_cannot_resume_existing_state(tmp_path: Path) -> None:
    run_experiment_batch(plan(), recording_adapters([]), config(), tmp_path)
    changed_plan = deepcopy(plan())
    changed_plan["title"] = "changed after execution"

    with pytest.raises(BatchExperimentError, match="plan changed"):
        run_experiment_batch(
            changed_plan,
            replay_adapters(changed_plan, replay()),
            config(),
            tmp_path,
        )


def test_budget_must_reserve_complete_matrix_before_execution(tmp_path: Path) -> None:
    calls: list[tuple[str, str, int]] = []
    value = config_mapping()
    value["maximum_total_cost"] = 7

    with pytest.raises(BatchExperimentError, match="reserve every declared run"):
        run_experiment_batch(plan(), recording_adapters(calls), config(value), tmp_path)

    assert calls == []


def test_run_budget_must_cover_complete_matrix_before_execution(tmp_path: Path) -> None:
    value = config_mapping()
    value["maximum_runs"] = 3
    value["maximum_runs_per_invocation"] = 2

    with pytest.raises(BatchExperimentError, match="maximum runs cannot cover"):
        run_experiment_batch(plan(), recording_adapters([]), config(value), tmp_path)


def test_cost_unit_must_match_experiment_metric(tmp_path: Path) -> None:
    value = config_mapping()
    value["cost_unit"] = "credits"

    with pytest.raises(BatchExperimentError, match="cost unit"):
        run_experiment_batch(plan(), recording_adapters([]), config(value), tmp_path)


def test_per_run_budget_violation_is_preserved_and_fails_closed(tmp_path: Path) -> None:
    selected_plan = plan()

    class ExpensiveAdapter:
        def run(self, arm, task, seed):
            return RunObservation(False, False, 0, 2.5, 1.0, 0, ("cost.json",))

    adapters = {
        arm["id"]: ExpensiveAdapter()
        for arm in [selected_plan["control"], *selected_plan["treatments"]]
    }

    with pytest.raises(BatchExperimentError, match="exceeded its declared budget"):
        run_experiment_batch(selected_plan, adapters, config(), tmp_path)

    state_path = tmp_path / config().batch_id / "batch-state.json"
    state = json.loads(state_path.read_text("utf-8"))
    assert state["status"] == "failed"
    assert state["spent_cost"] == 2.5
    assert state["cells"][0]["failure"] == "maximum_cost_per_run_exceeded"


@pytest.mark.parametrize(
    ("observation", "failure_code"),
    [
        (
            RunObservation(False, False, 0, 0.0, 151.0, 0, ("time.json",)),
            "maximum_time_per_run_exceeded",
        ),
        (
            RunObservation(False, False, 0, 0.0, 1.0, 2, ("human.json",)),
            "maximum_human_interventions_per_run_exceeded",
        ),
    ],
)
def test_other_per_run_budget_violations_fail_closed(
    tmp_path: Path, observation: RunObservation, failure_code: str
) -> None:
    selected_plan = plan()

    class FixedAdapter:
        def run(self, arm, task, seed):
            return observation

    adapters = {
        arm["id"]: FixedAdapter()
        for arm in [selected_plan["control"], *selected_plan["treatments"]]
    }

    with pytest.raises(BatchExperimentError, match="exceeded its declared budget"):
        run_experiment_batch(selected_plan, adapters, config(), tmp_path)

    state = json.loads(
        (tmp_path / config().batch_id / "batch-state.json").read_text("utf-8")
    )
    assert state["cells"][0]["failure"] == failure_code


def test_adapter_failure_records_only_error_type_and_releases_lock(tmp_path: Path) -> None:
    selected_plan = plan()

    class FailingAdapter:
        def run(self, arm, task, seed):
            raise RuntimeError("secret detail must not be persisted")

    adapters = {
        arm["id"]: FailingAdapter()
        for arm in [selected_plan["control"], *selected_plan["treatments"]]
    }

    with pytest.raises(RuntimeError, match="secret detail"):
        run_experiment_batch(selected_plan, adapters, config(), tmp_path)

    batch_dir = tmp_path / config().batch_id
    state = json.loads((batch_dir / "batch-state.json").read_text("utf-8"))
    assert state["cells"][0]["failure"] == "adapter_error:RuntimeError"
    assert "secret detail" not in json.dumps(state)
    assert not (batch_dir / "batch.lock").exists()


def test_existing_lock_prevents_concurrent_execution(tmp_path: Path) -> None:
    batch_dir = tmp_path / config().batch_id
    batch_dir.mkdir(parents=True)
    (batch_dir / "batch.lock").write_text("occupied", encoding="utf-8")

    with pytest.raises(BatchExperimentError, match="batch is locked"):
        run_experiment_batch(plan(), recording_adapters([]), config(), tmp_path)


def test_unknown_files_without_state_are_rejected(tmp_path: Path) -> None:
    batch_dir = tmp_path / config().batch_id
    batch_dir.mkdir(parents=True)
    (batch_dir / "orphan.txt").write_text("unknown", encoding="utf-8")

    with pytest.raises(BatchExperimentError, match="no trustworthy state"):
        run_experiment_batch(plan(), recording_adapters([]), config(), tmp_path)


def test_interrupted_running_cell_is_not_automatically_retried(tmp_path: Path) -> None:
    run_experiment_batch(plan(), recording_adapters([]), config(), tmp_path)
    state_path = tmp_path / config().batch_id / "batch-state.json"
    state = json.loads(state_path.read_text("utf-8"))
    pending = next(cell for cell in state["cells"] if cell["status"] == "pending")
    pending["status"] = "running"
    state["status"] = "running"
    state["pause_reason"] = None
    state_path.write_text(json.dumps(state), encoding="utf-8")

    with pytest.raises(BatchExperimentError, match="reconcile its evidence manually"):
        run_experiment_batch(plan(), recording_adapters([]), config(), tmp_path)


def test_tampered_aggregate_is_rejected(tmp_path: Path) -> None:
    run_experiment_batch(plan(), recording_adapters([]), config(), tmp_path)
    state_path = tmp_path / config().batch_id / "batch-state.json"
    state = json.loads(state_path.read_text("utf-8"))
    state["spent_cost"] += 1
    state_path.write_text(json.dumps(state), encoding="utf-8")

    with pytest.raises(BatchExperimentError, match="cost total is inconsistent"):
        run_experiment_batch(plan(), recording_adapters([]), config(), tmp_path)


def test_failed_cell_cannot_be_disguised_as_resumable(tmp_path: Path) -> None:
    run_experiment_batch(plan(), recording_adapters([]), config(), tmp_path)
    state_path = tmp_path / config().batch_id / "batch-state.json"
    state = json.loads(state_path.read_text("utf-8"))
    pending = next(cell for cell in state["cells"] if cell["status"] == "pending")
    pending["status"] = "failed"
    pending["failure"] = "adapter_error:RuntimeError"
    state_path.write_text(json.dumps(state), encoding="utf-8")

    with pytest.raises(BatchExperimentError, match="failed cell requires failed"):
        run_experiment_batch(plan(), recording_adapters([]), config(), tmp_path)


def test_tampered_completed_report_is_rejected(tmp_path: Path) -> None:
    adapters = recording_adapters([])
    run_experiment_batch(plan(), adapters, config(), tmp_path)
    completed = run_experiment_batch(plan(), adapters, config(), tmp_path)
    report = json.loads(completed.report_path.read_text("utf-8"))
    report["run_count"] = 999
    completed.report_path.write_text(json.dumps(report), encoding="utf-8")

    with pytest.raises(BatchExperimentError, match="report is inconsistent"):
        run_experiment_batch(plan(), adapters, config(), tmp_path)


def test_completed_batch_requires_its_report(tmp_path: Path) -> None:
    adapters = recording_adapters([])
    run_experiment_batch(plan(), adapters, config(), tmp_path)
    completed = run_experiment_batch(plan(), adapters, config(), tmp_path)
    completed.report_path.unlink()

    with pytest.raises(BatchExperimentError, match="missing its report"):
        run_experiment_batch(plan(), adapters, config(), tmp_path)


def test_batch_directory_link_is_rejected(tmp_path: Path) -> None:
    outside = tmp_path / "outside"
    outside.mkdir()
    run_root = tmp_path / "runs"
    run_root.mkdir()
    link = run_root / config().batch_id
    try:
        link.symlink_to(outside, target_is_directory=True)
    except OSError:
        pytest.skip("directory symlinks are unavailable")

    with pytest.raises(BatchExperimentError, match="filesystem link"):
        run_experiment_batch(plan(), recording_adapters([]), config(), run_root)


def test_cli_resumes_replay_batch(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    project = tmp_path / "project"
    (project / "examples").mkdir(parents=True)
    for name in (
        "batch-experiment.json",
        "experiment-record.json",
        "experiment-observations.json",
    ):
        (project / "examples" / name).write_bytes((ROOT / "examples" / name).read_bytes())

    arguments = [
        str(project / "examples" / "batch-experiment.json"),
        str(project / "examples" / "experiment-observations.json"),
        "--project-root",
        str(project),
    ]
    assert main(arguments) == 0
    first = json.loads(capsys.readouterr().out)
    assert main(arguments) == 0
    second = json.loads(capsys.readouterr().out)

    assert first["status"] == "paused"
    assert second["status"] == "completed"
    assert second["report_path"].endswith("experiment-report.json")


def test_cli_rejects_experiment_reference_outside_project(tmp_path: Path) -> None:
    project = tmp_path / "project"
    (project / "examples").mkdir(parents=True)
    config_value = config_mapping()
    config_value["experiment_ref"] = "../outside.json"
    config_path = project / "examples" / "batch-experiment.json"
    config_path.write_text(json.dumps(config_value), encoding="utf-8")
    observations_path = project / "examples" / "experiment-observations.json"
    observations_path.write_bytes(
        (ROOT / "examples" / "experiment-observations.json").read_bytes()
    )

    with pytest.raises(BatchExperimentError, match="escapes the project root"):
        main(
            [
                str(config_path),
                str(observations_path),
                "--project-root",
                str(project),
            ]
        )
