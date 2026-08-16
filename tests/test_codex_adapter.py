import json
import sys
from pathlib import Path

import pytest

from agentic_engineering.codex_adapter import (
    SUBMISSION_SCHEMA,
    CodexAdapterError,
    CodexExecConfig,
    CodexExecRunner,
    CodexExperimentAdapter,
    CostMeasurement,
    EvaluationOutcome,
    resolve_command_prefix,
)
from agentic_engineering.experiments import RunObservation, run_experiment

ROOT = Path(__file__).resolve().parents[1]
FAKE_CODEX = ROOT / "tests" / "fixtures" / "fake_codex.py"


def test_provider_schema_uses_supported_subset_and_parser_keeps_strictness() -> None:
    artifact_refs = SUBMISSION_SCHEMA["properties"]["artifact_refs"]

    assert "uniqueItems" not in artifact_refs


def test_windows_prefers_runnable_codex_cmd_shim() -> None:
    lookups: list[str] = []

    def resolver(name: str) -> str | None:
        lookups.append(name)
        return "C:/npm/codex.cmd" if name == "codex.cmd" else None

    resolved = resolve_command_prefix(
        ("codex", "fixture-argument"), platform_name="nt", resolver=resolver
    )

    assert resolved == ("C:/npm/codex.cmd", "fixture-argument")
    assert lookups == ["codex.cmd"]


def test_non_windows_command_prefix_is_unchanged() -> None:
    resolved = resolve_command_prefix(
        ("codex",), platform_name="posix", resolver=lambda name: "unexpected"
    )

    assert resolved == ("codex",)


def arm() -> dict:
    return {
        "id": "control",
        "workflow": "verified-single-agent",
        "config_ref": "configs/control.json",
    }


def task() -> dict:
    return {
        "id": "fixture-task",
        "repository": "fixture",
        "spec_ref": "specs/fixture.json",
    }


def runner(
    tmp_path: Path, *, mode: str = "normal", clock=None
) -> tuple[CodexExecRunner, Path]:
    workspace_root = tmp_path / "workspaces"
    workspace = workspace_root / "fixture"
    workspace.mkdir(parents=True)
    config = CodexExecConfig(
        command_prefix=(sys.executable, str(FAKE_CODEX), f"--fake-mode={mode}"),
        model="fixture-model",
        timeout_seconds=10,
    )
    kwargs = {"clock": clock} if clock is not None else {}
    return (
        CodexExecRunner(workspace_root, tmp_path / "evidence", config, **kwargs),
        workspace,
    )


def test_exec_uses_stdin_safe_sandbox_and_structured_output(tmp_path: Path) -> None:
    selected_runner, workspace = runner(tmp_path)

    result = selected_runner.execute(
        arm_id="control",
        task_id="fixture-task",
        seed=3,
        workspace=workspace,
        prompt="Execute one bounded agentic-engineering experiment cell. SECRET PROMPT",
    )

    transport = json.loads(result.stdout)
    request = json.loads((result.evidence_dir / "request.json").read_text("utf-8"))
    assert result.submission.claimed_complete is True
    assert result.model == "fixture-model"
    assert transport == {
        "prompt_from_stdin": True,
        "prompt_in_argv": False,
        "schema_exists": True,
        "json_mode": True,
        "auto_review": False,
        "sandbox_flag": True,
    }
    assert request["sandbox"] == "workspace-write"
    assert request["approval_mode"] == "none"
    assert "prompt" not in request
    assert len(result.evidence_refs) == 6


def test_executor_claim_cannot_verify_its_own_work(tmp_path: Path) -> None:
    times = iter([10.0, 12.5])
    selected_runner, workspace = runner(tmp_path, clock=lambda: next(times))

    class RejectingEvaluator:
        def evaluate(self, workspace, task, submission, evidence_dir):
            assert submission.claimed_complete is True
            return EvaluationOutcome(False, 1, ("audits/rejected.json",))

    class FixedCostMeter:
        def measure(self, result, arm, task, seed):
            return CostMeasurement(1.25, ("usage/control.json",))

    adapter = CodexExperimentAdapter(
        selected_runner,
        lambda arm, task, seed: workspace,
        RejectingEvaluator(),
        FixedCostMeter(),
    )
    treatment = {
        "id": "treatment",
        "workflow": "static-replay",
        "config_ref": "configs/treatment.json",
    }
    experiment = {
        "experiment_id": "adapter-integration",
        "status": "planned",
        "control": arm(),
        "treatments": [treatment],
        "tasks": [task()],
        "seeds": [3],
        "metrics": [
            {"id": "verified-completion", "direction": "higher"},
            {"id": "regressions", "direction": "lower"},
            {"id": "false-completion", "direction": "lower"},
            {"id": "cost", "direction": "lower"},
            {"id": "time", "direction": "lower"},
            {"id": "human-interventions", "direction": "lower"},
        ],
        "runs": [],
        "decision": {"adoption_rule": "treatment must improve verified completion"},
    }

    class StaticTreatment:
        def run(self, arm, task, seed):
            return RunObservation(
                False, False, 0, 0.5, 1.0, 0, ("replay/treatment.json",)
            )

    report = run_experiment(
        experiment, {"control": adapter, "treatment": StaticTreatment()}
    )
    observation = next(run for run in report["runs"] if run["arm_id"] == "control")

    assert observation["claimed_complete"] is True
    assert observation["results"] == {
        "verified-completion": 0.0,
        "regressions": 1,
        "false-completion": 1.0,
        "cost": 1.25,
        "time": 2.5,
        "human-interventions": 0,
    }
    assert "audits/rejected.json" in observation["evidence_refs"]
    assert "usage/control.json" in observation["evidence_refs"]


def test_unrestricted_sandbox_is_refused() -> None:
    with pytest.raises(CodexAdapterError, match="unrestricted modes are refused"):
        CodexExecConfig(sandbox="danger-full-access")


def test_auto_review_is_explicit_and_requires_workspace_write(tmp_path: Path) -> None:
    workspace_root = tmp_path / "workspaces"
    workspace = workspace_root / "fixture"
    workspace.mkdir(parents=True)
    selected_runner = CodexExecRunner(
        workspace_root,
        tmp_path / "evidence",
        CodexExecConfig(
            command_prefix=(sys.executable, str(FAKE_CODEX)),
            approve_for_me=True,
        ),
    )

    result = selected_runner.execute(
        arm_id="control",
        task_id="fixture-task",
        seed=0,
        workspace=workspace,
        prompt="bounded agentic-engineering task",
    )

    transport = json.loads(result.stdout)
    assert transport["auto_review"] is True
    assert transport["sandbox_flag"] is False
    request = json.loads((result.evidence_dir / "request.json").read_text("utf-8"))
    assert request["approval_mode"] == "auto-review"
    with pytest.raises(CodexAdapterError, match="requires the workspace-write"):
        CodexExecConfig(sandbox="read-only", approve_for_me=True)


def test_workspace_must_stay_inside_declared_root(tmp_path: Path) -> None:
    selected_runner, _ = runner(tmp_path)
    outside = tmp_path / "outside"
    outside.mkdir()

    with pytest.raises(CodexAdapterError, match="workspace escapes configured root"):
        selected_runner.execute(
            arm_id="control",
            task_id="fixture-task",
            seed=0,
            workspace=outside,
            prompt="bounded task",
        )


def test_failed_process_preserves_raw_output(tmp_path: Path) -> None:
    selected_runner, workspace = runner(tmp_path, mode="fail")

    with pytest.raises(CodexAdapterError, match="exited with code 7"):
        selected_runner.execute(
            arm_id="control",
            task_id="fixture-task",
            seed=0,
            workspace=workspace,
            prompt="bounded task",
        )

    evidence = tmp_path / "evidence" / "a-control__t-fixture-task__s-0"
    assert "simulated failure" in (evidence / "stderr.txt").read_text("utf-8")
    process = json.loads((evidence / "process.json").read_text("utf-8"))
    assert process["return_code"] == 7


def test_malformed_submission_is_rejected(tmp_path: Path) -> None:
    selected_runner, workspace = runner(tmp_path, mode="malformed")

    with pytest.raises(CodexAdapterError, match="valid JSON submission"):
        selected_runner.execute(
            arm_id="control",
            task_id="fixture-task",
            seed=0,
            workspace=workspace,
            prompt="bounded task",
        )


def test_evidence_for_a_cell_cannot_be_overwritten(tmp_path: Path) -> None:
    selected_runner, workspace = runner(tmp_path)
    arguments = {
        "arm_id": "control",
        "task_id": "fixture-task",
        "seed": 0,
        "workspace": workspace,
        "prompt": "bounded task",
    }
    selected_runner.execute(**arguments)

    with pytest.raises(CodexAdapterError, match="evidence already exists"):
        selected_runner.execute(**arguments)


def test_cost_must_come_from_valid_external_meter(tmp_path: Path) -> None:
    selected_runner, workspace = runner(tmp_path)

    class PassingEvaluator:
        def evaluate(self, workspace, task, submission, evidence_dir):
            return EvaluationOutcome(True, 0, ("audits/passed.json",))

    class InvalidCostMeter:
        def measure(self, result, arm, task, seed):
            return float("nan")

    adapter = CodexExperimentAdapter(
        selected_runner,
        lambda arm, task, seed: workspace,
        PassingEvaluator(),
        InvalidCostMeter(),
    )

    with pytest.raises(CodexAdapterError, match="non-negative finite"):
        adapter.run(arm(), task(), 0)


def test_structured_cost_measurement_requires_evidence(tmp_path: Path) -> None:
    selected_runner, workspace = runner(tmp_path)

    class PassingEvaluator:
        def evaluate(self, workspace, task, submission, evidence_dir):
            return EvaluationOutcome(True, 0, ("audits/passed.json",))

    class UnevidencedCostMeter:
        def measure(self, result, arm, task, seed):
            return CostMeasurement(1.0, ())

    adapter = CodexExperimentAdapter(
        selected_runner,
        lambda arm, task, seed: workspace,
        PassingEvaluator(),
        UnevidencedCostMeter(),
    )

    with pytest.raises(CodexAdapterError, match="requires evidence references"):
        adapter.run(arm(), task(), 0)
