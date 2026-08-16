"""Deterministic control/treatment experiments for agentic workflows."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Protocol


class ExperimentError(ValueError):
    """Raised when an experiment cannot be run as a complete fixed matrix."""


@dataclass(frozen=True)
class RunObservation:
    """Externally measured outcome from one arm/task/seed execution."""

    claimed_complete: bool
    verified_complete: bool
    regressions: int
    cost: float
    time_seconds: float
    human_interventions: int
    evidence_refs: tuple[str, ...]


class ExperimentAdapter(Protocol):
    """Execute one predeclared experiment cell."""

    def run(
        self, arm: Mapping[str, Any], task: Mapping[str, Any], seed: int
    ) -> RunObservation: ...


STANDARD_METRICS = {
    "verified-completion": "higher",
    "regressions": "lower",
    "false-completion": "lower",
    "cost": "lower",
    "time": "lower",
    "human-interventions": "lower",
}


def _canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"), sort_keys=True)


def _unique_ids(records: Sequence[Mapping[str, Any]], label: str) -> None:
    if any(not isinstance(record, Mapping) for record in records):
        raise ExperimentError(f"{label} entries must be objects")
    identifiers = [record.get("id") for record in records]
    if any(not isinstance(identifier, str) or not identifier for identifier in identifiers):
        raise ExperimentError(f"{label} require non-empty string IDs")
    if len(identifiers) != len(set(identifiers)):
        raise ExperimentError(f"duplicate {label} IDs")


def validate_experiment_plan(
    plan: Mapping[str, Any],
    adapters: Mapping[str, ExperimentAdapter] | None = None,
) -> None:
    if not isinstance(plan.get("experiment_id"), str) or not plan["experiment_id"]:
        raise ExperimentError("experiment requires a non-empty ID")
    if plan.get("status") != "planned":
        raise ExperimentError("experiment status must be planned")
    if plan.get("runs") != []:
        raise ExperimentError("planned experiment must not contain prior runs")

    control = plan.get("control")
    treatments = plan.get("treatments")
    tasks = plan.get("tasks")
    metrics = plan.get("metrics")
    seeds = plan.get("seeds")
    if not isinstance(control, Mapping):
        raise ExperimentError("experiment requires one control arm")
    if not isinstance(treatments, list) or not treatments:
        raise ExperimentError("experiment requires at least one treatment arm")
    if not isinstance(tasks, list) or not tasks:
        raise ExperimentError("experiment requires at least one task")
    if not isinstance(metrics, list):
        raise ExperimentError("experiment metrics must be a list")
    if (
        not isinstance(seeds, list)
        or not seeds
        or any(isinstance(seed, bool) or not isinstance(seed, int) or seed < 0 for seed in seeds)
        or len(seeds) != len(set(seeds))
    ):
        raise ExperimentError("seeds must be unique non-negative integers")

    arms = [control, *treatments]
    _unique_ids(arms, "arm")
    _unique_ids(tasks, "task")
    _unique_ids(metrics, "metric")

    metric_directions = {metric["id"]: metric.get("direction") for metric in metrics}
    missing_metrics = set(STANDARD_METRICS) - set(metric_directions)
    if missing_metrics:
        missing = ", ".join(sorted(missing_metrics))
        raise ExperimentError(f"experiment is missing standard metrics: {missing}")
    wrong_directions = {
        metric_id
        for metric_id, direction in STANDARD_METRICS.items()
        if metric_directions[metric_id] != direction
    }
    if wrong_directions:
        wrong = ", ".join(sorted(wrong_directions))
        raise ExperimentError(f"standard metric directions are invalid: {wrong}")
    unexpected_metrics = set(metric_directions) - set(STANDARD_METRICS)
    if unexpected_metrics:
        unexpected = ", ".join(sorted(unexpected_metrics))
        raise ExperimentError(f"unsupported experiment metrics: {unexpected}")

    decision = plan.get("decision")
    if (
        not isinstance(decision, Mapping)
        or not isinstance(decision.get("adoption_rule"), str)
        or not decision["adoption_rule"].strip()
    ):
        raise ExperimentError("experiment requires a predeclared adoption rule")

    if adapters is not None:
        arm_ids = {arm["id"] for arm in arms}
        adapter_ids = set(adapters)
        if any(not isinstance(adapter_id, str) or not adapter_id for adapter_id in adapter_ids):
            raise ExperimentError("adapter IDs must be non-empty strings")
        if adapter_ids != arm_ids:
            missing = ", ".join(sorted(arm_ids - adapter_ids)) or "none"
            unexpected = ", ".join(sorted(adapter_ids - arm_ids)) or "none"
            raise ExperimentError(
                "adapter IDs must match arm IDs; "
                f"missing: {missing}; unexpected: {unexpected}"
            )


def validate_run_observation(observation: RunObservation) -> None:
    if not isinstance(observation, RunObservation):
        raise ExperimentError("adapter returned an invalid observation")
    if not isinstance(observation.claimed_complete, bool) or not isinstance(
        observation.verified_complete, bool
    ):
        raise ExperimentError("completion fields must be booleans")
    for label, value in (
        ("regressions", observation.regressions),
        ("human interventions", observation.human_interventions),
    ):
        if isinstance(value, bool) or not isinstance(value, int) or value < 0:
            raise ExperimentError(f"{label} must be a non-negative integer")
    for label, value in (("cost", observation.cost), ("time", observation.time_seconds)):
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise ExperimentError(f"{label} must be a non-negative finite number")
        if not math.isfinite(value) or value < 0:
            raise ExperimentError(f"{label} must be a non-negative finite number")
    if not observation.evidence_refs:
        raise ExperimentError("every observation requires at least one evidence reference")
    if any(not isinstance(ref, str) or not ref for ref in observation.evidence_refs):
        raise ExperimentError("evidence references must be non-empty strings")
    if len(observation.evidence_refs) != len(set(observation.evidence_refs)):
        raise ExperimentError("evidence references must be unique")
    if observation.verified_complete and observation.regressions:
        raise ExperimentError("a verified completion cannot contain regressions")


def _mean(values: Sequence[float]) -> float:
    return round(math.fsum(values) / len(values), 12)


def _delta(treatment: float, control: float) -> float:
    value = round(treatment - control, 12)
    return 0.0 if value == 0 else value


def experiment_run_id(arm_id: str, task_id: str, seed: int) -> str:
    return f"run-a{len(arm_id)}-{arm_id}-t{len(task_id)}-{task_id}-s{seed}"


def experiment_plan_fingerprint(plan: Mapping[str, Any]) -> str:
    """Fingerprint the immutable planned matrix using canonical JSON."""

    return hashlib.sha256(_canonical_json(plan).encode("utf-8")).hexdigest()


def experiment_cells(
    plan: Mapping[str, Any],
) -> list[tuple[Mapping[str, Any], Mapping[str, Any], int]]:
    """Return the declared matrix in its deterministic execution order."""

    validate_experiment_plan(plan)
    arms = sorted([plan["control"], *plan["treatments"]], key=lambda arm: arm["id"])
    tasks = sorted(plan["tasks"], key=lambda task: task["id"])
    seeds = sorted(plan["seeds"])
    return [(arm, task, seed) for arm in arms for task in tasks for seed in seeds]


def _arm_summary(arm_id: str, runs: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    arm_runs = [run for run in runs if run["arm_id"] == arm_id]
    results = [run["results"] for run in arm_runs]
    false_completion_count = sum(
        int(result["false-completion"]) for result in results
    )
    regression_count = sum(int(result["regressions"]) for result in results)
    intervention_count = sum(
        int(result["human-interventions"]) for result in results
    )
    return {
        "arm_id": arm_id,
        "run_count": len(arm_runs),
        "verified_completion_rate": _mean(
            [result["verified-completion"] for result in results]
        ),
        "regression_count": regression_count,
        "mean_regressions": _mean([result["regressions"] for result in results]),
        "false_completion_count": false_completion_count,
        "false_completion_rate": _mean(
            [result["false-completion"] for result in results]
        ),
        "mean_cost": _mean([result["cost"] for result in results]),
        "mean_time_seconds": _mean([result["time"] for result in results]),
        "human_intervention_count": intervention_count,
        "mean_human_interventions": _mean(
            [result["human-interventions"] for result in results]
        ),
    }


def _comparison(control: Mapping[str, Any], treatment: Mapping[str, Any]) -> dict[str, Any]:
    completion_delta = _delta(
        treatment["verified_completion_rate"], control["verified_completion_rate"]
    )
    cost_delta = _delta(treatment["mean_cost"], control["mean_cost"])
    cost_per_success = (
        round(cost_delta / completion_delta, 12) if completion_delta > 0 else None
    )
    return {
        "control_arm_id": control["arm_id"],
        "treatment_arm_id": treatment["arm_id"],
        "paired_runs": treatment["run_count"],
        "deltas": {
            "verified_completion_rate": completion_delta,
            "mean_regressions": _delta(
                treatment["mean_regressions"], control["mean_regressions"]
            ),
            "false_completion_rate": _delta(
                treatment["false_completion_rate"], control["false_completion_rate"]
            ),
            "mean_cost": cost_delta,
            "mean_time_seconds": _delta(
                treatment["mean_time_seconds"], control["mean_time_seconds"]
            ),
            "mean_human_interventions": _delta(
                treatment["mean_human_interventions"],
                control["mean_human_interventions"],
            ),
        },
        "cost_per_additional_verified_completion": cost_per_success,
    }


def run_experiment(
    plan: Mapping[str, Any], adapters: Mapping[str, ExperimentAdapter]
) -> dict[str, Any]:
    """Run the complete declared matrix and return a deterministic report."""

    validate_experiment_plan(plan, adapters)
    arms = sorted([plan["control"], *plan["treatments"]], key=lambda arm: arm["id"])
    seeds = sorted(plan["seeds"])
    runs: list[dict[str, Any]] = []

    for arm, task, seed in experiment_cells(plan):
        observation = adapters[arm["id"]].run(arm, task, seed)
        validate_run_observation(observation)
        false_completion = bool(
            observation.claimed_complete and not observation.verified_complete
        )
        runs.append(
            {
                "id": experiment_run_id(arm["id"], task["id"], seed),
                "arm_id": arm["id"],
                "task_id": task["id"],
                "seed": seed,
                "claimed_complete": observation.claimed_complete,
                "results": {
                    "verified-completion": float(observation.verified_complete),
                    "regressions": observation.regressions,
                    "false-completion": float(false_completion),
                    "cost": float(observation.cost),
                    "time": float(observation.time_seconds),
                    "human-interventions": observation.human_interventions,
                },
                "evidence_refs": list(observation.evidence_refs),
            }
        )

    arm_summaries = [_arm_summary(arm["id"], runs) for arm in arms]
    summary_by_id = {summary["arm_id"]: summary for summary in arm_summaries}
    control_id = plan["control"]["id"]
    comparisons = [
        _comparison(summary_by_id[control_id], summary_by_id[treatment["id"]])
        for treatment in sorted(plan["treatments"], key=lambda arm: arm["id"])
    ]
    report: dict[str, Any] = {
        "version": 1,
        "experiment_id": plan["experiment_id"],
        "plan_fingerprint": experiment_plan_fingerprint(plan),
        "adoption_rule": plan["decision"]["adoption_rule"],
        "control_arm_id": control_id,
        "seeds": seeds,
        "run_count": len(runs),
        "matrix_complete": True,
        "runs": runs,
        "arm_summaries": arm_summaries,
        "comparisons": comparisons,
    }
    fingerprint = hashlib.sha256(_canonical_json(report).encode("utf-8")).hexdigest()
    report["report_id"] = f"experiment-report-{fingerprint[:16]}"
    report["fingerprint"] = fingerprint
    return report


class ReplayAdapter:
    """Replay fixed observations for reproducible harness tests and examples."""

    def __init__(self, observations: Mapping[tuple[str, str, int], RunObservation]):
        self.observations = dict(observations)

    def run(
        self, arm: Mapping[str, Any], task: Mapping[str, Any], seed: int
    ) -> RunObservation:
        key = (arm["id"], task["id"], seed)
        try:
            return self.observations[key]
        except KeyError as error:
            raise ExperimentError(f"missing replay observation: {key}") from error


def replay_adapters(
    plan: Mapping[str, Any], replay: Mapping[str, Any]
) -> dict[str, ReplayAdapter]:
    """Validate a replay matrix and build one adapter per declared arm."""

    validate_experiment_plan(plan)
    records = replay.get("observations")
    if not isinstance(records, list):
        raise ExperimentError("replay observations must be a list")
    observations: dict[tuple[str, str, int], RunObservation] = {}
    for record in records:
        if not isinstance(record, Mapping):
            raise ExperimentError("replay observations must be objects")
        key = (record.get("arm_id"), record.get("task_id"), record.get("seed"))
        if (
            not isinstance(key[0], str)
            or not key[0]
            or not isinstance(key[1], str)
            or not key[1]
            or isinstance(key[2], bool)
            or not isinstance(key[2], int)
            or key[2] < 0
        ):
            raise ExperimentError(f"invalid replay observation key: {key}")
        if key in observations:
            raise ExperimentError(f"duplicate replay observation: {key}")
        try:
            observation = RunObservation(
                claimed_complete=record["claimed_complete"],
                verified_complete=record["verified_complete"],
                regressions=record["regressions"],
                cost=record["cost"],
                time_seconds=record["time_seconds"],
                human_interventions=record["human_interventions"],
                evidence_refs=tuple(record["evidence_refs"]),
            )
        except (KeyError, TypeError) as error:
            raise ExperimentError(f"invalid replay observation: {key}") from error
        validate_run_observation(observation)
        observations[key] = observation

    arm_ids = [plan["control"]["id"], *[arm["id"] for arm in plan["treatments"]]]
    expected = {
        (arm_id, task["id"], seed)
        for arm_id in arm_ids
        for task in plan["tasks"]
        for seed in plan["seeds"]
    }
    actual = set(observations)
    if actual != expected:
        missing = sorted(expected - actual)
        unexpected = sorted(actual - expected)
        raise ExperimentError(
            f"replay matrix mismatch; missing: {missing}; unexpected: {unexpected}"
        )
    return {
        arm_id: ReplayAdapter(
            {key: value for key, value in observations.items() if key[0] == arm_id}
        )
        for arm_id in arm_ids
    }


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("plan", type=Path)
    parser.add_argument("observations", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    arguments = parser.parse_args(argv)

    plan = json.loads(arguments.plan.read_text(encoding="utf-8"))
    replay = json.loads(arguments.observations.read_text(encoding="utf-8"))
    report = run_experiment(plan, replay_adapters(plan, replay))
    arguments.output.parent.mkdir(parents=True, exist_ok=True)
    arguments.output.write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
