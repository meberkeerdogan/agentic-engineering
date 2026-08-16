import json
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator

from agentic_engineering.trajectory_capture import (
    TrajectoryCaptureError,
    capture_codex_trajectory,
    workspace_state_fingerprint,
)
from agentic_engineering.watchdog import analyze_trajectory


ROOT = Path(__file__).resolve().parents[1]


def jsonl_events(change_path: str = "app.py") -> str:
    events = [
        {
            "type": "item.completed",
            "item": {
                "id": "inspect-1",
                "type": "command_execution",
                "command": "rg app.py",
                "exit_code": 0,
                "status": "completed",
                "aggregated_output": "private inspection output",
            },
        },
        {
            "type": "item.completed",
            "item": {
                "id": "test-1",
                "type": "command_execution",
                "command": "python -m unittest -v test_app.py",
                "exit_code": 1,
                "status": "failed",
                "aggregated_output": "private failing output",
            },
        },
        {
            "type": "item.completed",
            "item": {
                "id": "change-1",
                "type": "file_change",
                "changes": [{"path": change_path, "kind": "update"}],
                "status": "completed",
            },
        },
        {
            "type": "item.completed",
            "item": {
                "id": "diff-1",
                "type": "command_execution",
                "command": "git diff -- app.py",
                "exit_code": 0,
                "status": "completed",
            },
        },
        {
            "type": "item.completed",
            "item": {
                "id": "test-2",
                "type": "command_execution",
                "command": "python -m unittest -v test_app.py",
                "exit_code": 0,
                "status": "completed",
            },
        },
        {"type": "turn.completed", "usage": {}},
    ]
    return "\n".join(json.dumps(event) for event in events) + "\n"


def capture_fixture(
    root: Path,
    *,
    change_path: str = "app.py",
    claimed_complete: bool = True,
    verified_complete: bool = True,
) -> tuple[dict, Path, Path]:
    workspace = root / "workspace"
    workspace.mkdir(parents=True)
    (workspace / "app.py").write_text("VALUE = 0\n", encoding="utf-8")
    (workspace / "test_app.py").write_text("# deterministic tests\n", encoding="utf-8")
    initial = workspace_state_fingerprint(workspace)
    (workspace / "app.py").write_text("VALUE = 1\n", encoding="utf-8")

    evidence_dir = root / "evidence" / "a-control__t-fixture__s-0"
    evidence_dir.mkdir(parents=True)
    (evidence_dir / "stdout.txt").write_text(
        jsonl_events(change_path), encoding="utf-8"
    )
    for name in (
        "final-message.json",
        "independent-evaluation.json",
        "evaluation-report.json",
    ):
        (evidence_dir / name).write_text("{}\n", encoding="utf-8")

    trajectory, _ = capture_codex_trajectory(
        cell_id="a-control__t-fixture__s-0",
        task_id="fixture",
        workspace=workspace,
        evidence_dir=evidence_dir,
        initial_state_fingerprint=initial,
        claimed_complete=claimed_complete,
        verified_complete=verified_complete,
    )
    return trajectory, workspace, evidence_dir


def test_capture_redacts_jsonl_and_maps_supported_phases(tmp_path: Path) -> None:
    trajectory, _, evidence_dir = capture_fixture(tmp_path)
    source = json.loads((evidence_dir / "trajectory-source.json").read_text("utf-8"))

    assert [event["phase"] for event in trajectory["events"]] == [
        "navigate",
        "reproduce",
        "patch",
        "navigate",
        "validate",
        "complete",
        "validate",
    ]
    assert [event["action"] for event in trajectory["events"]] == [
        "run_command",
        "run_tests",
        "edit",
        "inspect_diff",
        "run_tests",
        "claim_complete",
        "independent_audit_passed",
    ]
    assert trajectory["events"][0]["state_fingerprint"] == trajectory["events"][1][
        "state_fingerprint"
    ]
    assert trajectory["events"][2]["target"] == "app.py"
    assert source["ignored_event_count"] == 1
    assert len(source["records"]) == 5
    serialized_source = json.dumps(source)
    assert "private inspection output" not in serialized_source
    assert "private failing output" not in serialized_source
    assert "python -m unittest" not in serialized_source
    assert analyze_trajectory(trajectory)["signal_count"] == 0
    trajectory_schema = json.loads(
        (ROOT / "schemas" / "trajectory.schema.json").read_text("utf-8")
    )
    source_schema = json.loads(
        (ROOT / "schemas" / "trajectory-source.schema.json").read_text("utf-8")
    )
    assert not list(Draft202012Validator(trajectory_schema).iter_errors(trajectory))
    assert not list(Draft202012Validator(source_schema).iter_errors(source))


def test_capture_is_deterministic_and_preserves_evidence_refs(tmp_path: Path) -> None:
    first, _, first_evidence = capture_fixture(tmp_path / "first")
    second, _, second_evidence = capture_fixture(tmp_path / "second")

    assert first == second
    assert json.loads((first_evidence / "trajectory-source.json").read_text("utf-8")) == json.loads(
        (second_evidence / "trajectory-source.json").read_text("utf-8")
    )
    assert all(event["evidence_refs"] for event in first["events"])


def test_unclaimed_run_records_audit_without_completion_claim(tmp_path: Path) -> None:
    trajectory, _, _ = capture_fixture(
        tmp_path, claimed_complete=False, verified_complete=False
    )

    assert all(event["phase"] != "complete" for event in trajectory["events"])
    assert trajectory["events"][-1]["action"] == "independent_audit_failed"


def test_file_change_cannot_escape_workspace(tmp_path: Path) -> None:
    with pytest.raises(TrajectoryCaptureError, match="escapes the workspace"):
        capture_fixture(tmp_path, change_path="../outside.py")


def test_existing_trajectory_evidence_cannot_be_overwritten(tmp_path: Path) -> None:
    _, workspace, evidence_dir = capture_fixture(tmp_path)
    initial_source = (evidence_dir / "trajectory-source.json").read_bytes()

    with pytest.raises(TrajectoryCaptureError, match="already exists"):
        capture_codex_trajectory(
            cell_id="a-control__t-fixture__s-0",
            task_id="fixture",
            workspace=workspace,
            evidence_dir=evidence_dir,
            initial_state_fingerprint=workspace_state_fingerprint(workspace),
            claimed_complete=True,
            verified_complete=True,
        )

    assert (evidence_dir / "trajectory-source.json").read_bytes() == initial_source


def test_existing_trajectory_does_not_leave_partial_source_map(tmp_path: Path) -> None:
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    (workspace / "app.py").write_text("VALUE = 1\n", encoding="utf-8")
    evidence_dir = tmp_path / "evidence" / "a-control__t-fixture__s-0"
    evidence_dir.mkdir(parents=True)
    (evidence_dir / "stdout.txt").write_text("", encoding="utf-8")
    for name in (
        "final-message.json",
        "independent-evaluation.json",
        "evaluation-report.json",
    ):
        (evidence_dir / name).write_text("{}\n", encoding="utf-8")
    (evidence_dir / "trajectory.json").write_text("{}\n", encoding="utf-8")

    with pytest.raises(TrajectoryCaptureError, match="already exists"):
        capture_codex_trajectory(
            cell_id="a-control__t-fixture__s-0",
            task_id="fixture",
            workspace=workspace,
            evidence_dir=evidence_dir,
            initial_state_fingerprint=workspace_state_fingerprint(workspace),
            claimed_complete=False,
            verified_complete=False,
        )

    assert not (evidence_dir / "trajectory-source.json").exists()


def test_invalid_jsonl_is_rejected(tmp_path: Path) -> None:
    _, workspace, evidence_dir = capture_fixture(tmp_path)
    (evidence_dir / "trajectory.json").unlink()
    (evidence_dir / "trajectory-source.json").unlink()
    (evidence_dir / "stdout.txt").write_text("{invalid}\n", encoding="utf-8")

    with pytest.raises(TrajectoryCaptureError, match="line 1 is invalid"):
        capture_codex_trajectory(
            cell_id="a-control__t-fixture__s-0",
            task_id="fixture",
            workspace=workspace,
            evidence_dir=evidence_dir,
            initial_state_fingerprint=workspace_state_fingerprint(workspace),
            claimed_complete=True,
            verified_complete=True,
        )


def test_workspace_fingerprint_ignores_test_caches(tmp_path: Path) -> None:
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    (workspace / "app.py").write_text("VALUE = 1\n", encoding="utf-8")
    before = workspace_state_fingerprint(workspace)
    cache = workspace / "__pycache__"
    cache.mkdir()
    (cache / "app.pyc").write_bytes(b"cache")

    assert workspace_state_fingerprint(workspace) == before
