"""One supported product interface for the verified single-agent workflow."""

from __future__ import annotations

import json
import subprocess
from collections.abc import Callable, Mapping
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any

from .live_pilot import LivePilotError, run_live_pilot
from .state_store import StateTransitionError, VerifiedStateStore


class ProductRunError(RuntimeError):
    """Raised when the supported product workflow cannot finish safely."""


WORKFLOW_ID = "verified-single-agent-v0.1"


def _load_object(path: Path, label: str) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        raise ProductRunError(f"{label} is not valid UTF-8 JSON: {path}") from error
    if not isinstance(value, dict):
        raise ProductRunError(f"{label} must be a JSON object")
    return value


def _write_json(path: Path, value: Any) -> None:
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


def _resolve_inside(root: Path, reference: str, label: str) -> Path:
    if not isinstance(reference, str) or not reference:
        raise ProductRunError(f"{label} must be a non-empty relative path")
    path = Path(reference)
    if path.is_absolute():
        raise ProductRunError(f"{label} must be relative to the project root")
    root = root.resolve()
    candidate = (root / path).resolve()
    try:
        candidate.relative_to(root)
    except ValueError as error:
        raise ProductRunError(f"{label} escapes the project root") from error
    return candidate


def _run_git(workspace: Path, *arguments: str, accepted: set[int] | None = None) -> str:
    completed = subprocess.run(
        ["git", *arguments],
        cwd=workspace,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        shell=False,
        check=False,
    )
    allowed = accepted or {0}
    if completed.returncode not in allowed:
        detail = completed.stderr.strip() or completed.stdout.strip()
        raise ProductRunError(f"could not capture workspace revision: {detail}")
    return completed.stdout.strip()


def _capture_revision(workspace: Path) -> str:
    _run_git(workspace, "add", "--all")
    changed = subprocess.run(
        ["git", "diff", "--cached", "--quiet"],
        cwd=workspace,
        shell=False,
        check=False,
    ).returncode
    if changed == 1:
        _run_git(
            workspace,
            "-c",
            "user.name=Agentic Engineering",
            "-c",
            "user.email=product@agentic-engineering.invalid",
            "commit",
            "--quiet",
            "-m",
            "Capture verified workflow result",
        )
    elif changed != 0:
        raise ProductRunError("could not inspect the final workspace revision")
    revision = _run_git(workspace, "rev-parse", "HEAD")
    return f"git-{revision}"


def _evidence_ref(summary: Mapping[str, Any], suffix: str) -> str:
    matches = [
        reference
        for reference in summary.get("evidence_refs", [])
        if isinstance(reference, str) and reference.endswith(suffix)
    ]
    if len(matches) != 1:
        raise ProductRunError(f"run did not produce exactly one {suffix} evidence file")
    return matches[0]


def _now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def run_verified_workflow(
    project_root: Path,
    config_path: Path,
    run_id: str,
    *,
    confirm_paid_run: bool,
    command_prefix: tuple[str, ...] = ("codex",),
    source_codex_home: Path | None = None,
    preflight_date: date | None = None,
    timestamp: Callable[[], str] = _now,
) -> dict[str, Any]:
    """Run the frozen v0.1 workflow and return one inspectable summary."""

    if confirm_paid_run is not True:
        raise ProductRunError(
            "live execution requires --confirm-paid-run because it may spend credits"
        )
    project_root = project_root.resolve()
    config_path = config_path.resolve()
    config = _load_object(config_path, "product run config")
    if config.get("spec_history_ref") is None:
        raise ProductRunError("product runs require a specification history reference")
    arm = config.get("arm")
    if not isinstance(arm, Mapping) or arm.get("workflow") != WORKFLOW_ID:
        raise ProductRunError(f"product runs require workflow {WORKFLOW_ID}")

    try:
        pilot = run_live_pilot(
            project_root,
            config_path,
            run_id,
            command_prefix=command_prefix,
            source_codex_home=source_codex_home,
            preflight_date=preflight_date,
        )
    except (LivePilotError, StateTransitionError) as error:
        raise ProductRunError(str(error)) from error

    run_root = _resolve_inside(project_root, config["run_root_ref"], "run root")
    run_dir = _resolve_inside(run_root, run_id, "run directory")
    task = config["task"]
    workspace = _resolve_inside(
        run_dir / "workspaces", task["id"], "workspace"
    )
    active_spec_path = _resolve_inside(
        workspace, task["spec_ref"], "compiled specification"
    )
    active_spec = _load_object(active_spec_path, "compiled specification")
    evaluation_ref = _evidence_ref(pilot, "evaluation-report.json")
    submission_ref = _evidence_ref(pilot, "final-message.json")
    evaluation = _load_object(run_dir / "evidence" / evaluation_ref, "evaluation report")
    submission = _load_object(run_dir / "evidence" / submission_ref, "executor submission")
    revision = _capture_revision(workspace)

    state_log = run_dir / "verified-state.jsonl"
    store = VerifiedStateStore(state_log)
    recorded_at = timestamp()
    try:
        store.create(
            run_id,
            active_spec["id"],
            [{"id": task["id"], "depends_on": []}],
            recorded_at,
        )
        store.start(task["id"], timestamp())
        store.submit(
            task["id"],
            list(submission["artifact_refs"]),
            submission["summary"],
            timestamp(),
        )
        final_state = store.record_evaluation(
            task["id"], evaluation, revision, timestamp()
        )
    except (KeyError, StateTransitionError) as error:
        raise ProductRunError(f"could not record verified state: {error}") from error

    _write_json(run_dir / "active-spec.json", active_spec)
    _write_json(run_dir / "verified-state.json", final_state)
    summary = {
        "version": 1,
        "workflow_id": WORKFLOW_ID,
        "run_id": run_id,
        "status": final_state["status"],
        "task_id": task["id"],
        "spec_id": active_spec["id"],
        "claimed_complete": pilot["claimed_complete"],
        "verified_complete": final_state["status"] == "verified",
        "regressions": pilot["regressions"],
        "scores": evaluation.get("scores"),
        "measured_cost": pilot["measured_cost"],
        "cost_unit": pilot["cost_unit"],
        "time_seconds": pilot["time_seconds"],
        "workspace_revision": revision,
        "active_spec_ref": "active-spec.json",
        "evaluation_ref": f"evidence/{evaluation_ref}",
        "state_ref": "verified-state.json",
        "state_log_ref": "verified-state.jsonl",
        "pilot_summary_ref": "pilot-summary.json",
        "evidence_refs": pilot["evidence_refs"],
    }
    _write_json(run_dir / "product-summary.json", summary)
    return summary
