"""Redacted, observe-only trajectory capture for live Codex experiment cells."""

from __future__ import annotations

import hashlib
import json
import re
from collections.abc import Mapping
from pathlib import Path
from typing import Any


class TrajectoryCaptureError(ValueError):
    """Raised when live evidence cannot produce a trustworthy trajectory."""


TRAJECTORY_CAPTURE_VERSION = 1
ID_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")
IGNORED_PARTS = {".git", "__pycache__", ".pytest_cache"}


def _canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"), sort_keys=True)


def _fingerprint(value: Any) -> str:
    return hashlib.sha256(_canonical_json(value).encode("utf-8")).hexdigest()


def _is_link(path: Path) -> bool:
    is_junction = getattr(path, "is_junction", lambda: False)
    return path.is_symlink() or is_junction()


def workspace_state_fingerprint(workspace: Path) -> str:
    """Fingerprint durable workspace files while excluding Git and test caches."""

    if _is_link(workspace):
        raise TrajectoryCaptureError("trajectory workspace must be a real directory")
    workspace = workspace.resolve()
    if not workspace.is_dir():
        raise TrajectoryCaptureError("trajectory workspace must be a real directory")
    entries: list[dict[str, Any]] = []
    for path in sorted(
        workspace.rglob("*"), key=lambda item: item.relative_to(workspace).as_posix()
    ):
        relative = path.relative_to(workspace)
        if any(part in IGNORED_PARTS for part in relative.parts):
            continue
        if path.suffix == ".pyc":
            continue
        if _is_link(path):
            raise TrajectoryCaptureError("trajectory workspaces may not contain links")
        if not path.is_file():
            continue
        try:
            content = path.read_bytes()
        except OSError as error:
            raise TrajectoryCaptureError(
                f"could not fingerprint workspace file: {relative.as_posix()}"
            ) from error
        entries.append(
            {
                "path": relative.as_posix(),
                "bytes": len(content),
                "sha256": hashlib.sha256(content).hexdigest(),
            }
        )
    return _fingerprint(entries)


def _resolve_change_path(workspace: Path, value: Any) -> str:
    if not isinstance(value, str) or not value:
        raise TrajectoryCaptureError("file-change paths must be non-empty strings")
    path = Path(value)
    candidate = path.resolve() if path.is_absolute() else (workspace / path).resolve()
    try:
        relative = candidate.relative_to(workspace)
    except ValueError as error:
        raise TrajectoryCaptureError("file-change path escapes the workspace") from error
    return relative.as_posix()


def _classify_command(command: str, patch_seen: bool) -> tuple[str, str, str]:
    lowered = command.casefold()
    if "unittest" in lowered or "pytest" in lowered:
        return (
            "validate" if patch_seen else "reproduce",
            "run_tests",
            "test-suite",
        )
    if "git diff" in lowered or "git status" in lowered:
        return "navigate", "inspect_diff", "workspace"
    return "navigate", "run_command", "repository"


def _write_new_json(path: Path, value: Any) -> None:
    try:
        with path.open("x", encoding="utf-8", newline="\n") as stream:
            json.dump(value, stream, ensure_ascii=False, indent=2)
            stream.write("\n")
    except FileExistsError as error:
        raise TrajectoryCaptureError(
            f"trajectory evidence already exists: {path.name}"
        ) from error


def capture_codex_trajectory(
    *,
    cell_id: str,
    task_id: str,
    workspace: Path,
    evidence_dir: Path,
    initial_state_fingerprint: str,
    claimed_complete: bool,
    verified_complete: bool,
) -> tuple[dict[str, Any], tuple[str, str]]:
    """Create a redacted M07 trajectory plus its JSONL provenance map."""

    for value, label in ((cell_id, "cell ID"), (task_id, "task ID")):
        if not isinstance(value, str) or not ID_PATTERN.fullmatch(value):
            raise TrajectoryCaptureError(f"{label} must be path-safe")
    if not re.fullmatch(r"[a-f0-9]{64}", initial_state_fingerprint):
        raise TrajectoryCaptureError("initial state fingerprint must be SHA-256")
    if not isinstance(claimed_complete, bool) or not isinstance(verified_complete, bool):
        raise TrajectoryCaptureError("completion observations must be booleans")
    if _is_link(workspace) or _is_link(evidence_dir):
        raise TrajectoryCaptureError(
            "workspace and evidence directory must be real directories"
        )
    workspace = workspace.resolve()
    evidence_dir = evidence_dir.resolve()
    if not workspace.is_dir() or not evidence_dir.is_dir():
        raise TrajectoryCaptureError("workspace and evidence directory must exist")

    stdout_path = evidence_dir / "stdout.txt"
    final_path = evidence_dir / "final-message.json"
    independent_path = evidence_dir / "independent-evaluation.json"
    evaluation_path = evidence_dir / "evaluation-report.json"
    for path in (stdout_path, final_path, independent_path, evaluation_path):
        if not path.is_file() or _is_link(path):
            raise TrajectoryCaptureError(
                f"required trajectory evidence is missing: {path.name}"
            )
    try:
        stdout = stdout_path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as error:
        raise TrajectoryCaptureError("Codex JSONL is not readable UTF-8") from error

    trajectory_id = f"trajectory-{cell_id}"
    evidence_root = evidence_dir.parent
    source_path = evidence_dir / "trajectory-source.json"
    trajectory_path = evidence_dir / "trajectory.json"
    for path in (source_path, trajectory_path):
        if path.exists() or _is_link(path):
            raise TrajectoryCaptureError(
                f"trajectory evidence already exists: {path.name}"
            )
    source_ref = source_path.relative_to(evidence_root).as_posix()
    raw_stdout_ref = stdout_path.relative_to(evidence_root).as_posix()
    current_state = initial_state_fingerprint
    patch_seen = False
    ignored_event_count = 0
    events: list[dict[str, Any]] = []
    records: list[dict[str, Any]] = []

    for line_number, raw_line in enumerate(stdout.splitlines(), start=1):
        if not raw_line.strip():
            continue
        try:
            event = json.loads(raw_line)
        except json.JSONDecodeError as error:
            raise TrajectoryCaptureError(
                f"Codex JSONL line {line_number} is invalid"
            ) from error
        if not isinstance(event, Mapping):
            raise TrajectoryCaptureError(
                f"Codex JSONL line {line_number} must contain an object"
            )
        item = event.get("item")
        if event.get("type") != "item.completed" or not isinstance(item, Mapping):
            ignored_event_count += 1
            continue
        item_type = item.get("type")
        if item_type == "command_execution":
            command = item.get("command")
            exit_code = item.get("exit_code")
            if not isinstance(command, str) or not command:
                raise TrajectoryCaptureError("completed command item has no command")
            if isinstance(exit_code, bool) or not isinstance(exit_code, int):
                raise TrajectoryCaptureError("completed command item has no exit code")
            phase, action, target = _classify_command(command, patch_seen)
            record_details = {"exit_code": exit_code, "changed_paths": []}
        elif item_type == "file_change":
            changes = item.get("changes")
            if not isinstance(changes, list) or not changes:
                raise TrajectoryCaptureError("completed file-change item has no changes")
            normalized_changes: list[dict[str, str]] = []
            for change in changes:
                if not isinstance(change, Mapping):
                    raise TrajectoryCaptureError("file-change entries must be objects")
                kind = change.get("kind")
                if not isinstance(kind, str) or not kind:
                    raise TrajectoryCaptureError("file-change kind must be non-empty")
                normalized_changes.append(
                    {
                        "path": _resolve_change_path(workspace, change.get("path")),
                        "kind": kind,
                    }
                )
            normalized_changes.sort(key=lambda change: (change["path"], change["kind"]))
            current_state = _fingerprint(
                {"previous_state": current_state, "changes": normalized_changes}
            )
            patch_seen = True
            phase, action = "patch", "edit"
            changed_paths = sorted({change["path"] for change in normalized_changes})
            target = ",".join(changed_paths)
            record_details = {
                "exit_code": None,
                "changed_paths": changed_paths,
            }
        else:
            ignored_event_count += 1
            continue

        step = len(events) + 1
        record_id = f"record-{len(records) + 1:03d}"
        evidence_ref = f"{source_ref}#{record_id}"
        records.append(
            {
                "id": record_id,
                "trajectory_step": step,
                "jsonl_line": line_number,
                "event_type": "item.completed",
                "item_type": item_type,
                "item_id": item.get("id") if isinstance(item.get("id"), str) else None,
                "status": item.get("status") if isinstance(item.get("status"), str) else None,
                "action": action,
                "target": target,
                **record_details,
            }
        )
        events.append(
            {
                "step": step,
                "phase": phase,
                "action": action,
                "target": target,
                "state_fingerprint": current_state,
                "evidence_refs": [evidence_ref],
            }
        )

    final_state = workspace_state_fingerprint(workspace)
    if not patch_seen and final_state != initial_state_fingerprint:
        events.append(
            {
                "step": len(events) + 1,
                "phase": "patch",
                "action": "observed_workspace_change",
                "target": "workspace",
                "state_fingerprint": final_state,
                "evidence_refs": [raw_stdout_ref],
            }
        )
    if claimed_complete:
        events.append(
            {
                "step": len(events) + 1,
                "phase": "complete",
                "action": "claim_complete",
                "target": task_id,
                "state_fingerprint": final_state,
                "evidence_refs": [final_path.relative_to(evidence_root).as_posix()],
            }
        )
    events.append(
        {
            "step": len(events) + 1,
            "phase": "validate",
            "action": (
                "independent_audit_passed"
                if verified_complete
                else "independent_audit_failed"
            ),
            "target": task_id,
            "state_fingerprint": final_state,
            "evidence_refs": [
                independent_path.relative_to(evidence_root).as_posix(),
                evaluation_path.relative_to(evidence_root).as_posix(),
            ],
        }
    )

    source = {
        "version": 1,
        "capture_version": TRAJECTORY_CAPTURE_VERSION,
        "trajectory_id": trajectory_id,
        "source": "codex-jsonl-item.completed",
        "raw_stdout_ref": raw_stdout_ref,
        "raw_stdout_sha256": hashlib.sha256(stdout.encode("utf-8")).hexdigest(),
        "ignored_event_count": ignored_event_count,
        "records": records,
    }
    trajectory = {
        "version": 1,
        "trajectory_id": trajectory_id,
        "task_id": task_id,
        "events": events,
    }
    _write_new_json(source_path, source)
    _write_new_json(trajectory_path, trajectory)
    return trajectory, (
        trajectory_path.relative_to(evidence_root).as_posix(),
        source_ref,
    )
