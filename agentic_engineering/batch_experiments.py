"""Budgeted, resumable execution of a declared experiment matrix."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import re
import socket
import sys
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .experiments import (
    ExperimentAdapter,
    ExperimentError,
    RunObservation,
    experiment_cells,
    experiment_plan_fingerprint,
    experiment_run_id,
    replay_adapters,
    run_experiment,
    validate_experiment_plan,
    validate_run_observation,
)


class BatchExperimentError(ExperimentError):
    """Raised when a batch cannot proceed without risking invalid evidence or spend."""


ID_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")
CONFIG_FIELDS = {
    "version",
    "batch_id",
    "experiment_ref",
    "run_root_ref",
    "cost_unit",
    "maximum_runs",
    "maximum_runs_per_invocation",
    "maximum_total_cost",
    "maximum_cost_per_run",
    "maximum_total_time_seconds",
    "maximum_time_per_run_seconds",
    "maximum_human_interventions",
    "maximum_human_interventions_per_run",
}
STATE_FIELDS = {
    "version",
    "batch_id",
    "status",
    "plan_fingerprint",
    "config_fingerprint",
    "matrix_size",
    "completed_count",
    "spent_cost",
    "spent_time_seconds",
    "human_interventions",
    "pause_reason",
    "report_ref",
    "cells",
}
CELL_FIELDS = {
    "id",
    "arm_id",
    "task_id",
    "seed",
    "status",
    "observation",
    "failure",
}
OBSERVATION_FIELDS = {
    "claimed_complete",
    "verified_complete",
    "regressions",
    "cost",
    "time_seconds",
    "human_interventions",
    "evidence_refs",
}


def _canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"), sort_keys=True)


def _fingerprint(value: Any) -> str:
    return hashlib.sha256(_canonical_json(value).encode("utf-8")).hexdigest()


def _non_negative_number(value: Any, label: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise BatchExperimentError(f"{label} must be a non-negative finite number")
    if not math.isfinite(value) or value < 0:
        raise BatchExperimentError(f"{label} must be a non-negative finite number")
    return float(value)


def _positive_integer(value: Any, label: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
        raise BatchExperimentError(f"{label} must be a positive integer")
    return value


def _non_negative_integer(value: Any, label: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise BatchExperimentError(f"{label} must be a non-negative integer")
    return value


@dataclass(frozen=True)
class BatchExperimentConfig:
    """Immutable limits and storage references for one experiment batch."""

    batch_id: str
    experiment_ref: str
    run_root_ref: str
    cost_unit: str
    maximum_runs: int
    maximum_runs_per_invocation: int
    maximum_total_cost: float
    maximum_cost_per_run: float
    maximum_total_time_seconds: float
    maximum_time_per_run_seconds: float
    maximum_human_interventions: int
    maximum_human_interventions_per_run: int
    fingerprint: str

    @classmethod
    def from_mapping(cls, value: Mapping[str, Any]) -> "BatchExperimentConfig":
        if set(value) != CONFIG_FIELDS or value.get("version") != 1:
            raise BatchExperimentError(
                "batch config must contain exactly the version 1 fields"
            )
        batch_id = value.get("batch_id")
        if not isinstance(batch_id, str) or not ID_PATTERN.fullmatch(batch_id):
            raise BatchExperimentError("batch ID must be a path-safe ID")
        for field in ("experiment_ref", "run_root_ref", "cost_unit"):
            if not isinstance(value.get(field), str) or not value[field]:
                raise BatchExperimentError(f"{field} must be a non-empty string")
        maximum_runs = _positive_integer(value.get("maximum_runs"), "maximum runs")
        per_invocation = _positive_integer(
            value.get("maximum_runs_per_invocation"),
            "maximum runs per invocation",
        )
        if per_invocation > maximum_runs:
            raise BatchExperimentError(
                "maximum runs per invocation may not exceed maximum runs"
            )
        total_cost = _non_negative_number(
            value.get("maximum_total_cost"), "maximum total cost"
        )
        per_run_cost = _non_negative_number(
            value.get("maximum_cost_per_run"), "maximum cost per run"
        )
        total_time = _non_negative_number(
            value.get("maximum_total_time_seconds"), "maximum total time"
        )
        per_run_time = _non_negative_number(
            value.get("maximum_time_per_run_seconds"), "maximum time per run"
        )
        total_interventions = _non_negative_integer(
            value.get("maximum_human_interventions"),
            "maximum human interventions",
        )
        per_run_interventions = _non_negative_integer(
            value.get("maximum_human_interventions_per_run"),
            "maximum human interventions per run",
        )
        return cls(
            batch_id=batch_id,
            experiment_ref=value["experiment_ref"],
            run_root_ref=value["run_root_ref"],
            cost_unit=value["cost_unit"],
            maximum_runs=maximum_runs,
            maximum_runs_per_invocation=per_invocation,
            maximum_total_cost=total_cost,
            maximum_cost_per_run=per_run_cost,
            maximum_total_time_seconds=total_time,
            maximum_time_per_run_seconds=per_run_time,
            maximum_human_interventions=total_interventions,
            maximum_human_interventions_per_run=per_run_interventions,
            fingerprint=_fingerprint(value),
        )


@dataclass(frozen=True)
class BatchOutcome:
    status: str
    completed_count: int
    matrix_size: int
    spent_cost: float
    spent_time_seconds: float
    human_interventions: int
    state_path: Path
    report_path: Path | None


class _BatchLock:
    def __init__(self, path: Path):
        self.path = path
        self.acquired = False

    def __enter__(self) -> "_BatchLock":
        payload = _canonical_json(
            {"version": 1, "pid": os.getpid(), "host": socket.gethostname()}
        )
        try:
            descriptor = os.open(self.path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
        except FileExistsError as error:
            raise BatchExperimentError(
                "batch is locked; verify no runner is active before removing the lock"
            ) from error
        try:
            os.write(descriptor, payload.encode("utf-8"))
            os.fsync(descriptor)
        finally:
            os.close(descriptor)
        self.acquired = True
        return self

    def __exit__(self, exc_type: Any, exc_value: Any, traceback: Any) -> None:
        if self.acquired:
            self.path.unlink()
            self.acquired = False


def _write_json_atomic(path: Path, value: Any) -> None:
    temporary = path.with_name(f".{path.name}.{os.getpid()}.tmp")
    encoded = json.dumps(value, ensure_ascii=False, indent=2) + "\n"
    try:
        with temporary.open("x", encoding="utf-8", newline="\n") as stream:
            stream.write(encoded)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if temporary.exists():
            temporary.unlink()


def _load_object(path: Path, label: str) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        raise BatchExperimentError(f"{label} is not valid UTF-8 JSON") from error
    if not isinstance(value, dict):
        raise BatchExperimentError(f"{label} must be a JSON object")
    return value


def _observation_to_mapping(observation: RunObservation) -> dict[str, Any]:
    return {
        "claimed_complete": observation.claimed_complete,
        "verified_complete": observation.verified_complete,
        "regressions": observation.regressions,
        "cost": float(observation.cost),
        "time_seconds": float(observation.time_seconds),
        "human_interventions": observation.human_interventions,
        "evidence_refs": list(observation.evidence_refs),
    }


def _observation_from_mapping(value: Mapping[str, Any]) -> RunObservation:
    if set(value) != OBSERVATION_FIELDS:
        raise BatchExperimentError("stored observation fields are invalid")
    try:
        observation = RunObservation(
            claimed_complete=value["claimed_complete"],
            verified_complete=value["verified_complete"],
            regressions=value["regressions"],
            cost=value["cost"],
            time_seconds=value["time_seconds"],
            human_interventions=value["human_interventions"],
            evidence_refs=tuple(value["evidence_refs"]),
        )
    except TypeError as error:
        raise BatchExperimentError("stored observation is invalid") from error
    validate_run_observation(observation)
    return observation


def _new_state(
    plan: Mapping[str, Any], config: BatchExperimentConfig
) -> dict[str, Any]:
    cells = [
        {
            "id": experiment_run_id(arm["id"], task["id"], seed),
            "arm_id": arm["id"],
            "task_id": task["id"],
            "seed": seed,
            "status": "pending",
            "observation": None,
            "failure": None,
        }
        for arm, task, seed in experiment_cells(plan)
    ]
    return {
        "version": 1,
        "batch_id": config.batch_id,
        "status": "planned",
        "plan_fingerprint": experiment_plan_fingerprint(plan),
        "config_fingerprint": config.fingerprint,
        "matrix_size": len(cells),
        "completed_count": 0,
        "spent_cost": 0.0,
        "spent_time_seconds": 0.0,
        "human_interventions": 0,
        "pause_reason": None,
        "report_ref": None,
        "cells": cells,
    }


def _totals(cells: Sequence[Mapping[str, Any]]) -> tuple[int, float, float, int]:
    observations = [
        _observation_from_mapping(cell["observation"])
        for cell in cells
        if isinstance(cell.get("observation"), Mapping)
    ]
    completed = sum(cell.get("status") == "completed" for cell in cells)
    return (
        completed,
        math.fsum(observation.cost for observation in observations),
        math.fsum(observation.time_seconds for observation in observations),
        sum(observation.human_interventions for observation in observations),
    )


def _validate_state(
    state: Mapping[str, Any],
    plan: Mapping[str, Any],
    config: BatchExperimentConfig,
) -> None:
    if set(state) != STATE_FIELDS or state.get("version") != 1:
        raise BatchExperimentError("batch state fields are invalid")
    if state.get("batch_id") != config.batch_id:
        raise BatchExperimentError("batch state belongs to another batch ID")
    if state.get("plan_fingerprint") != experiment_plan_fingerprint(plan):
        raise BatchExperimentError("experiment plan changed after the batch started")
    if state.get("config_fingerprint") != config.fingerprint:
        raise BatchExperimentError("batch config changed after the batch started")
    if state.get("status") not in {"planned", "running", "paused", "completed", "failed"}:
        raise BatchExperimentError("batch state has an invalid status")
    if state.get("pause_reason") not in {None, "invocation_run_limit"}:
        raise BatchExperimentError("batch state has an invalid pause reason")
    if state.get("report_ref") not in {None, "experiment-report.json"}:
        raise BatchExperimentError("batch state has an invalid report reference")
    cells = state.get("cells")
    expected = [
        (experiment_run_id(arm["id"], task["id"], seed), arm["id"], task["id"], seed)
        for arm, task, seed in experiment_cells(plan)
    ]
    if not isinstance(cells, list) or len(cells) != len(expected):
        raise BatchExperimentError("batch state matrix is incomplete")
    for cell, identity in zip(cells, expected, strict=True):
        if not isinstance(cell, Mapping) or set(cell) != CELL_FIELDS:
            raise BatchExperimentError("batch cell fields are invalid")
        if (cell["id"], cell["arm_id"], cell["task_id"], cell["seed"]) != identity:
            raise BatchExperimentError("batch cell identity does not match the plan")
        if cell["status"] not in {"pending", "running", "completed", "failed"}:
            raise BatchExperimentError("batch cell has an invalid status")
        if cell["status"] == "completed" and not isinstance(cell["observation"], Mapping):
            raise BatchExperimentError("completed batch cell is missing its observation")
        if cell["status"] in {"pending", "running"} and cell["observation"] is not None:
            raise BatchExperimentError("unfinished batch cell contains an observation")
        if cell["observation"] is not None:
            if not isinstance(cell["observation"], Mapping):
                raise BatchExperimentError("batch cell observation must be an object or null")
            _observation_from_mapping(cell["observation"])
        if cell["failure"] is not None and (
            not isinstance(cell["failure"], str) or not cell["failure"]
        ):
            raise BatchExperimentError("batch cell failure must be a non-empty string or null")
        if cell["status"] == "failed" and cell["failure"] is None:
            raise BatchExperimentError("failed batch cell is missing its failure code")
        if cell["status"] != "failed" and cell["failure"] is not None:
            raise BatchExperimentError("non-failed batch cell contains a failure code")
    completed, cost, elapsed, interventions = _totals(cells)
    if (
        isinstance(state.get("matrix_size"), bool)
        or not isinstance(state.get("matrix_size"), int)
        or isinstance(state.get("completed_count"), bool)
        or not isinstance(state.get("completed_count"), int)
        or state["matrix_size"] != len(expected)
        or state["completed_count"] != completed
    ):
        raise BatchExperimentError("batch state counts are inconsistent")
    for stored, derived, label in (
        (state.get("spent_cost"), cost, "cost"),
        (state.get("spent_time_seconds"), elapsed, "time"),
    ):
        if (
            isinstance(stored, bool)
            or not isinstance(stored, (int, float))
            or not math.isclose(float(stored), derived, rel_tol=0, abs_tol=1e-12)
        ):
            raise BatchExperimentError(f"batch state {label} total is inconsistent")
    if (
        isinstance(state.get("human_interventions"), bool)
        or not isinstance(state.get("human_interventions"), int)
        or state["human_interventions"] != interventions
    ):
        raise BatchExperimentError("batch state intervention total is inconsistent")
    statuses = [cell["status"] for cell in cells]
    if statuses.count("running") > 1:
        raise BatchExperimentError("batch state contains multiple running cells")
    if "failed" in statuses and state["status"] != "failed":
        raise BatchExperimentError("failed cell requires failed batch status")
    if state["status"] == "planned" and any(status != "pending" for status in statuses):
        raise BatchExperimentError("planned batch contains started cells")
    if state["status"] == "completed" and any(status != "completed" for status in statuses):
        raise BatchExperimentError("completed batch contains unfinished cells")
    if state["status"] == "paused" and "running" in statuses:
        raise BatchExperimentError("paused batch contains a running cell")
    if state["status"] == "failed" and "failed" not in statuses:
        raise BatchExperimentError("failed batch contains no failed cell")
    if state["status"] == "completed" and state["report_ref"] != "experiment-report.json":
        raise BatchExperimentError("completed batch is missing its report reference")
    if state["status"] != "completed" and state["report_ref"] is not None:
        raise BatchExperimentError("unfinished batch contains a report reference")


def _refresh_totals(state: dict[str, Any]) -> None:
    completed, cost, elapsed, interventions = _totals(state["cells"])
    state["completed_count"] = completed
    state["spent_cost"] = cost
    state["spent_time_seconds"] = elapsed
    state["human_interventions"] = interventions


def _validate_budget_capacity(
    plan: Mapping[str, Any], config: BatchExperimentConfig
) -> None:
    matrix_size = len(experiment_cells(plan))
    cost_metrics = [metric for metric in plan["metrics"] if metric["id"] == "cost"]
    if len(cost_metrics) != 1 or cost_metrics[0].get("unit") != config.cost_unit:
        raise BatchExperimentError("batch cost unit does not match the experiment metric")
    if config.maximum_runs < matrix_size:
        raise BatchExperimentError("maximum runs cannot cover the declared matrix")
    if config.maximum_total_cost < config.maximum_cost_per_run * matrix_size:
        raise BatchExperimentError("total cost budget cannot reserve every declared run")
    if (
        config.maximum_total_time_seconds
        < config.maximum_time_per_run_seconds * matrix_size
    ):
        raise BatchExperimentError("total time budget cannot reserve every declared run")
    if (
        config.maximum_human_interventions
        < config.maximum_human_interventions_per_run * matrix_size
    ):
        raise BatchExperimentError(
            "human-intervention budget cannot reserve every declared run"
        )


def _check_observation_budget(
    observation: RunObservation, config: BatchExperimentConfig
) -> str | None:
    if observation.cost > config.maximum_cost_per_run:
        return "maximum_cost_per_run_exceeded"
    if observation.time_seconds > config.maximum_time_per_run_seconds:
        return "maximum_time_per_run_exceeded"
    if observation.human_interventions > config.maximum_human_interventions_per_run:
        return "maximum_human_interventions_per_run_exceeded"
    return None


def _outcome(state: Mapping[str, Any], state_path: Path, report_path: Path) -> BatchOutcome:
    return BatchOutcome(
        status=state["status"],
        completed_count=state["completed_count"],
        matrix_size=state["matrix_size"],
        spent_cost=float(state["spent_cost"]),
        spent_time_seconds=float(state["spent_time_seconds"]),
        human_interventions=state["human_interventions"],
        state_path=state_path,
        report_path=report_path if report_path.is_file() else None,
    )


def _report_from_state(
    plan: Mapping[str, Any], state: Mapping[str, Any]
) -> dict[str, Any]:
    observations = []
    for cell in state["cells"]:
        if cell["status"] != "completed" or not isinstance(cell["observation"], Mapping):
            raise BatchExperimentError("cannot build a report from an incomplete matrix")
        observations.append(
            {
                "arm_id": cell["arm_id"],
                "task_id": cell["task_id"],
                "seed": cell["seed"],
                **cell["observation"],
            }
        )
    replay = {"version": 1, "observations": observations}
    return run_experiment(plan, replay_adapters(plan, replay))


def run_experiment_batch(
    plan: Mapping[str, Any],
    adapters: Mapping[str, ExperimentAdapter],
    config: BatchExperimentConfig,
    run_root: Path,
) -> BatchOutcome:
    """Run or resume one bounded chunk without repeating completed cells."""

    validate_experiment_plan(plan, adapters)
    _validate_budget_capacity(plan, config)
    run_root = run_root.resolve()
    run_root.mkdir(parents=True, exist_ok=True)
    batch_dir = run_root / config.batch_id
    is_junction = getattr(batch_dir, "is_junction", lambda: False)
    if batch_dir.exists() and (batch_dir.is_symlink() or is_junction()):
        raise BatchExperimentError("batch directory may not be a filesystem link")
    batch_dir.mkdir(exist_ok=True)
    if not batch_dir.is_dir() or batch_dir.resolve().parent != run_root:
        raise BatchExperimentError("batch directory escapes the configured run root")
    state_path = batch_dir / "batch-state.json"
    report_path = batch_dir / "experiment-report.json"
    lock_path = batch_dir / "batch.lock"
    if state_path.is_symlink() or report_path.is_symlink():
        raise BatchExperimentError("batch evidence files may not be filesystem links")

    with _BatchLock(lock_path):
        if state_path.exists():
            state = _load_object(state_path, "batch state")
            _validate_state(state, plan, config)
        else:
            if any(path != lock_path for path in batch_dir.iterdir()):
                raise BatchExperimentError(
                    "batch directory contains files but no trustworthy state"
                )
            state = _new_state(plan, config)
            _write_json_atomic(state_path, state)

        if state["status"] == "completed":
            if not report_path.is_file():
                raise BatchExperimentError("completed batch is missing its report")
            stored_report = _load_object(report_path, "experiment report")
            if stored_report != _report_from_state(plan, state):
                raise BatchExperimentError("completed experiment report is inconsistent")
            return _outcome(state, state_path, report_path)
        if state["status"] == "failed":
            raise BatchExperimentError("failed batch requires manual investigation")
        running = [cell["id"] for cell in state["cells"] if cell["status"] == "running"]
        if running:
            raise BatchExperimentError(
                f"cell {running[0]} was interrupted in progress; reconcile its evidence manually"
            )

        arm_by_id = {
            arm["id"]: arm for arm in [plan["control"], *plan["treatments"]]
        }
        task_by_id = {task["id"]: task for task in plan["tasks"]}
        executed = 0
        state["status"] = "running"
        state["pause_reason"] = None
        _write_json_atomic(state_path, state)

        for cell in state["cells"]:
            if cell["status"] == "completed":
                continue
            if executed >= config.maximum_runs_per_invocation:
                state["status"] = "paused"
                state["pause_reason"] = "invocation_run_limit"
                _write_json_atomic(state_path, state)
                return _outcome(state, state_path, report_path)

            cell["status"] = "running"
            _write_json_atomic(state_path, state)
            try:
                observation = adapters[cell["arm_id"]].run(
                    arm_by_id[cell["arm_id"]],
                    task_by_id[cell["task_id"]],
                    cell["seed"],
                )
                validate_run_observation(observation)
            except Exception as error:
                cell["status"] = "failed"
                cell["failure"] = f"adapter_error:{type(error).__name__}"
                state["status"] = "failed"
                _write_json_atomic(state_path, state)
                raise

            cell["observation"] = _observation_to_mapping(observation)
            violation = _check_observation_budget(observation, config)
            if violation is not None:
                cell["status"] = "failed"
                cell["failure"] = violation
                state["status"] = "failed"
                _refresh_totals(state)
                _write_json_atomic(state_path, state)
                raise BatchExperimentError(f"cell {cell['id']} exceeded its declared budget")
            cell["status"] = "completed"
            cell["failure"] = None
            executed += 1
            _refresh_totals(state)
            _write_json_atomic(state_path, state)

        report = _report_from_state(plan, state)
        _write_json_atomic(report_path, report)
        state["status"] = "completed"
        state["pause_reason"] = None
        state["report_ref"] = report_path.name
        _write_json_atomic(state_path, state)
        return _outcome(state, state_path, report_path)


def _resolve_inside(root: Path, reference: str, label: str) -> Path:
    candidate_path = Path(reference)
    if candidate_path.is_absolute():
        raise BatchExperimentError(f"{label} must be relative to the project root")
    root = root.resolve()
    candidate = (root / candidate_path).resolve()
    try:
        candidate.relative_to(root)
    except ValueError as error:
        raise BatchExperimentError(f"{label} escapes the project root") from error
    return candidate


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("config", type=Path)
    parser.add_argument("observations", type=Path)
    parser.add_argument("--project-root", type=Path, default=Path.cwd())
    arguments = parser.parse_args(argv)

    root = arguments.project_root.resolve()
    config_path = arguments.config.resolve()
    observations_path = arguments.observations.resolve()
    for path, label in (
        (config_path, "batch config"),
        (observations_path, "replay observations"),
    ):
        try:
            path.relative_to(root)
        except ValueError as error:
            raise BatchExperimentError(f"{label} must be inside the project root") from error
    config_mapping = _load_object(config_path, "batch config")
    config = BatchExperimentConfig.from_mapping(config_mapping)
    plan_path = _resolve_inside(root, config.experiment_ref, "experiment reference")
    run_root = _resolve_inside(root, config.run_root_ref, "run-root reference")
    plan = _load_object(plan_path, "experiment plan")
    replay = _load_object(observations_path, "replay observations")
    outcome = run_experiment_batch(plan, replay_adapters(plan, replay), config, run_root)
    json.dump(
        {
            "status": outcome.status,
            "completed_count": outcome.completed_count,
            "matrix_size": outcome.matrix_size,
            "spent_cost": outcome.spent_cost,
            "spent_time_seconds": outcome.spent_time_seconds,
            "human_interventions": outcome.human_interventions,
            "state_path": outcome.state_path.relative_to(root).as_posix(),
            "report_path": (
                outcome.report_path.relative_to(root).as_posix()
                if outcome.report_path is not None
                else None
            ),
        },
        sys.stdout,
        ensure_ascii=False,
        indent=2,
    )
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
