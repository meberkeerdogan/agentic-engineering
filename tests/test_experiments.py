import json
from copy import deepcopy
from pathlib import Path

import pytest
from test_core_schemas import load_json

from agentic_engineering.experiments import (
    ExperimentError,
    ReplayAdapter,
    RunObservation,
    main,
    replay_adapters,
    run_experiment,
)

ROOT = Path(__file__).resolve().parents[1]


def plan() -> dict:
    return load_json("examples/experiment-record.json")


def replay() -> dict:
    return load_json("examples/experiment-observations.json")


def adapters(experiment: dict | None = None) -> dict[str, ReplayAdapter]:
    selected_plan = experiment or plan()
    return replay_adapters(selected_plan, replay())


def test_fixture_produces_exact_golden_report() -> None:
    experiment = plan()

    report = run_experiment(experiment, adapters(experiment))

    assert report == load_json("examples/expected-experiment-report.json")


def test_repeated_runs_are_byte_stable() -> None:
    experiment = plan()

    first = run_experiment(experiment, adapters(experiment))
    second = run_experiment(experiment, adapters(experiment))

    assert json.dumps(first, sort_keys=True) == json.dumps(second, sort_keys=True)


def test_matrix_order_is_deterministic() -> None:
    experiment = plan()
    experiment["seeds"] = list(reversed(experiment["seeds"]))
    seen: list[tuple[str, str, int]] = []

    class RecordingAdapter:
        def run(self, arm, task, seed):
            seen.append((arm["id"], task["id"], seed))
            return RunObservation(
                claimed_complete=False,
                verified_complete=False,
                regressions=0,
                cost=0.0,
                time_seconds=0.0,
                human_interventions=0,
                evidence_refs=(f"evidence/{arm['id']}-{task['id']}-{seed}.json",),
            )

    adapter_map = {
        arm["id"]: RecordingAdapter()
        for arm in [experiment["control"], *experiment["treatments"]]
    }

    run_experiment(experiment, adapter_map)

    assert seen == sorted(seen)


def test_run_ids_do_not_collide_for_ambiguous_arm_and_task_names() -> None:
    experiment = plan()
    experiment["control"]["id"] = "a-b"
    experiment["treatments"][0]["id"] = "a"
    experiment["tasks"] = [
        {"id": "c", "repository": "repo", "spec_ref": "spec-c.json"},
        {"id": "b-c", "repository": "repo", "spec_ref": "spec-b-c.json"},
    ]

    class StaticAdapter:
        def run(self, arm, task, seed):
            return RunObservation(
                claimed_complete=False,
                verified_complete=False,
                regressions=0,
                cost=0.0,
                time_seconds=0.0,
                human_interventions=0,
                evidence_refs=(f"evidence/{arm['id']}-{task['id']}-{seed}.json",),
            )

    report = run_experiment(
        experiment, {"a-b": StaticAdapter(), "a": StaticAdapter()}
    )
    run_ids = [run["id"] for run in report["runs"]]

    assert len(run_ids) == len(set(run_ids))


def test_false_completion_is_derived_from_claim_and_verification() -> None:
    experiment = plan()
    report = run_experiment(experiment, adapters(experiment))

    control_first = report["runs"][0]

    assert control_first["claimed_complete"] is True
    assert control_first["results"]["verified-completion"] == 0.0
    assert control_first["results"]["false-completion"] == 1.0


def test_invalid_plan_is_rejected_before_any_adapter_runs() -> None:
    experiment = plan()
    experiment["metrics"] = [
        metric
        for metric in experiment["metrics"]
        if metric["id"] != "false-completion"
    ]
    calls = 0

    class CountingAdapter:
        def run(self, arm, task, seed):
            nonlocal calls
            calls += 1
            raise AssertionError("adapter should not run")

    adapter_map = {
        arm["id"]: CountingAdapter()
        for arm in [experiment["control"], *experiment["treatments"]]
    }

    with pytest.raises(ExperimentError, match="missing standard metrics"):
        run_experiment(experiment, adapter_map)

    assert calls == 0


def test_plan_requires_a_predeclared_adoption_rule() -> None:
    experiment = plan()
    experiment["decision"]["adoption_rule"] = ""

    with pytest.raises(ExperimentError, match="predeclared adoption rule"):
        replay_adapters(experiment, replay())


def test_replay_matrix_must_be_complete_before_execution() -> None:
    fixture = replay()
    fixture["observations"].pop()

    with pytest.raises(ExperimentError, match="replay matrix mismatch"):
        replay_adapters(plan(), fixture)


def test_replay_matrix_rejects_duplicate_cells() -> None:
    fixture = replay()
    fixture["observations"].append(deepcopy(fixture["observations"][0]))

    with pytest.raises(ExperimentError, match="duplicate replay observation"):
        replay_adapters(plan(), fixture)


def test_observation_requires_external_evidence() -> None:
    experiment = plan()

    class UnevidencedAdapter:
        def run(self, arm, task, seed):
            return RunObservation(
                claimed_complete=True,
                verified_complete=True,
                regressions=0,
                cost=1.0,
                time_seconds=1.0,
                human_interventions=0,
                evidence_refs=(),
            )

    adapter_map = {
        arm["id"]: UnevidencedAdapter()
        for arm in [experiment["control"], *experiment["treatments"]]
    }

    with pytest.raises(ExperimentError, match="evidence reference"):
        run_experiment(experiment, adapter_map)


def test_verified_completion_cannot_contain_regressions() -> None:
    experiment = plan()

    class ContradictoryAdapter:
        def run(self, arm, task, seed):
            return RunObservation(
                claimed_complete=True,
                verified_complete=True,
                regressions=1,
                cost=1.0,
                time_seconds=1.0,
                human_interventions=0,
                evidence_refs=("evidence/contradictory.json",),
            )

    adapter_map = {
        arm["id"]: ContradictoryAdapter()
        for arm in [experiment["control"], *experiment["treatments"]]
    }

    with pytest.raises(ExperimentError, match="cannot contain regressions"):
        run_experiment(experiment, adapter_map)


def test_comparison_does_not_invent_cost_per_success_without_a_gain() -> None:
    experiment = plan()
    fixture = replay()
    for observation in fixture["observations"]:
        observation["verified_complete"] = True
        observation["regressions"] = 0
    report = run_experiment(experiment, replay_adapters(experiment, fixture))

    assert report["comparisons"][0]["deltas"]["verified_completion_rate"] == 0.0
    assert (
        report["comparisons"][0]["cost_per_additional_verified_completion"] is None
    )


def test_duplicate_adapter_registration_is_rejected_before_execution() -> None:
    experiment = deepcopy(plan())
    experiment["treatments"][0]["id"] = experiment["control"]["id"]

    with pytest.raises(ExperimentError, match="duplicate arm IDs"):
        run_experiment(experiment, {experiment["control"]["id"]: object()})


def test_cli_writes_golden_report(tmp_path: Path) -> None:
    output = tmp_path / "experiment-report.json"

    exit_code = main(
        [
            str(ROOT / "examples" / "experiment-record.json"),
            str(ROOT / "examples" / "experiment-observations.json"),
            "--output",
            str(output),
        ]
    )

    assert exit_code == 0
    assert json.loads(output.read_text(encoding="utf-8")) == load_json(
        "examples/expected-experiment-report.json"
    )
