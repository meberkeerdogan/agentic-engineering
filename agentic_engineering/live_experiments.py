"""Run a resumable control/treatment matrix through isolated Codex cells."""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
import sys
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any

from .batch_experiments import (
    BatchExperimentConfig,
    BatchOutcome,
    run_experiment_batch,
)
from .codex_adapter import (
    ID_PATTERN,
    SAFE_SANDBOXES,
    CodexAdapterError,
    CodexExecConfig,
    CodexExecRunner,
    CodexExperimentAdapter,
    require_approve_for_me_support,
    resolve_command_prefix,
)
from .codex_environment import (
    VERSION_PATTERN,
    CodexEnvironmentPolicy,
    TemporaryCodexHome,
    run_codex_preflight,
)
from .codex_evidence import EvidenceContractEvaluator, JsonlUsageCostMeter, UsageRates
from .experiments import RunObservation, validate_experiment_plan


class LiveExperimentError(CodexAdapterError):
    """Raised when a live batch cannot be prepared without contaminating evidence."""


CONFIG_FIELDS = {
    "version",
    "batch_ref",
    "rates_ref",
    "environment_ref",
    "model",
    "sandbox",
    "approval_mode",
    "timeout_seconds",
    "task_bindings",
}
TASK_BINDING_FIELDS = {"id", "evidence_contract_ref"}
RATE_FIELDS = {
    "version",
    "model",
    "unit",
    "effective_date",
    "source_url",
    "input_per_million",
    "cached_input_per_million",
    "output_per_million",
}


def _canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"), sort_keys=True)


def _fingerprint(value: Any) -> str:
    return hashlib.sha256(_canonical_json(value).encode("utf-8")).hexdigest()


def _storage_id(cell_id: str) -> str:
    """Keep nested Git paths short while retaining the full ID in evidence."""

    return f"c-{hashlib.sha256(cell_id.encode('utf-8')).hexdigest()[:16]}"


def _write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


def _load_object(path: Path, label: str) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        raise LiveExperimentError(f"{label} is not valid UTF-8 JSON") from error
    if not isinstance(value, dict):
        raise LiveExperimentError(f"{label} must be a JSON object")
    return value


def _resolve_inside(root: Path, reference: str, label: str) -> Path:
    if not isinstance(reference, str) or not reference:
        raise LiveExperimentError(f"{label} must be a non-empty relative path")
    path = Path(reference)
    if path.is_absolute():
        raise LiveExperimentError(f"{label} must be relative to the project root")
    root = root.resolve()
    candidate = (root / path).resolve()
    try:
        candidate.relative_to(root)
    except ValueError as error:
        raise LiveExperimentError(f"{label} escapes the project root") from error
    return candidate


def _is_link(path: Path) -> bool:
    is_junction = getattr(path, "is_junction", lambda: False)
    return path.is_symlink() or is_junction()


def _safe_direct_child_directory(root: Path, name: str) -> Path:
    root = root.resolve()
    path = root / name
    if path.exists() and _is_link(path):
        raise LiveExperimentError(f"{name} may not be a filesystem link")
    path.mkdir(parents=True, exist_ok=True)
    if not path.is_dir() or path.resolve().parent != root:
        raise LiveExperimentError(f"{name} escapes the batch directory")
    return path


def _template_snapshot(template: Path) -> dict[str, Any]:
    if not template.is_dir():
        raise LiveExperimentError(f"task repository template does not exist: {template}")
    if _is_link(template):
        raise LiveExperimentError("task repository templates may not be filesystem links")
    entries: list[dict[str, Any]] = []
    for path in sorted(template.rglob("*"), key=lambda item: item.relative_to(template).as_posix()):
        relative = path.relative_to(template).as_posix()
        if path.name == ".git" or "/.git/" in f"/{relative}/":
            raise LiveExperimentError("task repository templates may not contain Git metadata")
        if _is_link(path):
            raise LiveExperimentError("task repository templates may not contain filesystem links")
        if path.is_dir():
            entries.append({"path": relative, "type": "directory"})
        elif path.is_file():
            try:
                content = path.read_bytes()
            except OSError as error:
                raise LiveExperimentError(f"could not read task template file: {relative}") from error
            entries.append(
                {
                    "path": relative,
                    "type": "file",
                    "bytes": len(content),
                    "sha256": hashlib.sha256(content).hexdigest(),
                }
            )
        else:
            raise LiveExperimentError(f"task template contains an unsupported entry: {relative}")
    return {"version": 1, "entries": entries, "fingerprint": _fingerprint(entries)}


def _run_git(workspace: Path, *arguments: str) -> None:
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
    if completed.returncode != 0:
        raise LiveExperimentError("could not initialize an isolated experiment repository")


def _probe_executor_version(
    command_prefix: tuple[str, ...], project_root: Path, timeout_seconds: float
) -> str:
    try:
        completed = subprocess.run(
            [*resolve_command_prefix(command_prefix), "--version"],
            cwd=project_root,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            shell=False,
            timeout=timeout_seconds,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired) as error:
        raise LiveExperimentError("could not inspect the Codex executor version") from error
    if completed.returncode != 0:
        raise LiveExperimentError("Codex executor version inspection failed")
    match = VERSION_PATTERN.search(completed.stdout + completed.stderr)
    if not match:
        raise LiveExperimentError("Codex executor version output was not recognized")
    return ".".join(match.groups())


def _initialize_workspace(workspace: Path) -> None:
    _run_git(workspace, "init", "--quiet")
    _run_git(workspace, "add", "--all")
    _run_git(
        workspace,
        "-c",
        "user.name=Agentic Engineering Experiment",
        "-c",
        "user.email=experiment@agentic-engineering.invalid",
        "commit",
        "--quiet",
        "-m",
        "Seed isolated experiment fixture",
    )


@dataclass(frozen=True)
class LiveExperimentConfig:
    """Committed launcher settings shared by every cell in one live batch."""

    batch_ref: str
    rates_ref: str
    environment_ref: str
    model: str
    sandbox: str
    approval_mode: str
    timeout_seconds: float
    task_bindings: Mapping[str, str]

    @classmethod
    def from_mapping(cls, value: Mapping[str, Any]) -> "LiveExperimentConfig":
        if set(value) != CONFIG_FIELDS or value.get("version") != 1:
            raise LiveExperimentError(
                "live experiment config must contain exactly the version 1 fields"
            )
        for field in ("batch_ref", "rates_ref", "environment_ref", "model"):
            if not isinstance(value.get(field), str) or not value[field]:
                raise LiveExperimentError(f"{field} must be a non-empty string")
        if value.get("sandbox") not in SAFE_SANDBOXES:
            raise LiveExperimentError("live experiment sandbox must be safe")
        if value.get("approval_mode") not in {"none", "auto-review"}:
            raise LiveExperimentError(
                "live experiment approval mode must be none or auto-review"
            )
        if (
            value["sandbox"] == "workspace-write"
            and value["approval_mode"] != "auto-review"
        ):
            raise LiveExperimentError("workspace-write experiments require auto-review")
        if value["sandbox"] == "read-only" and value["approval_mode"] != "none":
            raise LiveExperimentError("read-only experiments cannot enable auto-review")
        timeout = value.get("timeout_seconds")
        if (
            isinstance(timeout, bool)
            or not isinstance(timeout, (int, float))
            or timeout <= 0
            or timeout > 3600
        ):
            raise LiveExperimentError("live experiment timeout must be from 0 to 3600 seconds")
        records = value.get("task_bindings")
        if not isinstance(records, list) or not records:
            raise LiveExperimentError("live experiment requires task bindings")
        bindings: dict[str, str] = {}
        for record in records:
            if not isinstance(record, Mapping) or set(record) != TASK_BINDING_FIELDS:
                raise LiveExperimentError("task binding fields are invalid")
            task_id = record.get("id")
            evidence_ref = record.get("evidence_contract_ref")
            if not isinstance(task_id, str) or not ID_PATTERN.fullmatch(task_id):
                raise LiveExperimentError("task binding ID must be path-safe")
            if task_id in bindings:
                raise LiveExperimentError("task binding IDs must be unique")
            if not isinstance(evidence_ref, str) or not evidence_ref:
                raise LiveExperimentError("evidence contract reference must be non-empty")
            bindings[task_id] = evidence_ref
        return cls(
            batch_ref=value["batch_ref"],
            rates_ref=value["rates_ref"],
            environment_ref=value["environment_ref"],
            model=value["model"],
            sandbox=value["sandbox"],
            approval_mode=value["approval_mode"],
            timeout_seconds=float(timeout),
            task_bindings=bindings,
        )


class LiveCodexBatchAdapter:
    """Prepare, preflight, execute, and independently evaluate one live cell."""

    def __init__(
        self,
        *,
        project_root: Path,
        batch_dir: Path,
        config: LiveExperimentConfig,
        rates: UsageRates,
        environment_policy: CodexEnvironmentPolicy,
        template_snapshots: Mapping[str, Mapping[str, Any]],
        workflow_refs: tuple[str, ...],
        command_prefix: tuple[str, ...],
        source_codex_home: Path | None,
        preflight_date: date | None,
    ):
        self.project_root = project_root
        self.batch_dir = batch_dir
        self.config = config
        self.rates = rates
        self.environment_policy = environment_policy
        self.template_snapshots = template_snapshots
        self.workflow_refs = workflow_refs
        self.command_prefix = command_prefix
        self.source_codex_home = source_codex_home
        self.preflight_date = preflight_date

    def run(
        self, arm: Mapping[str, Any], task: Mapping[str, Any], seed: int
    ) -> RunObservation:
        arm_id = arm.get("id")
        task_id = task.get("id")
        if not isinstance(arm_id, str) or not ID_PATTERN.fullmatch(arm_id):
            raise LiveExperimentError("arm ID must be path-safe")
        if not isinstance(task_id, str) or not ID_PATTERN.fullmatch(task_id):
            raise LiveExperimentError("task ID must be path-safe")
        if isinstance(seed, bool) or not isinstance(seed, int) or seed < 0:
            raise LiveExperimentError("seed must be a non-negative integer")
        cell_id = f"a-{arm_id}__t-{task_id}__s-{seed}"
        template = _resolve_inside(
            self.project_root, task.get("repository"), "task repository reference"
        )
        current_snapshot = _template_snapshot(template)
        expected_snapshot = self.template_snapshots.get(task_id)
        if current_snapshot != expected_snapshot:
            raise LiveExperimentError("task repository template changed after batch binding")

        workspace_root = _safe_direct_child_directory(
            self.batch_dir, "live-workspaces"
        )
        workspace = workspace_root / _storage_id(cell_id)
        if workspace.exists() or _is_link(workspace):
            raise LiveExperimentError(f"live workspace already exists for cell: {cell_id}")
        shutil.copytree(template, workspace)
        if _template_snapshot(workspace) != expected_snapshot:
            raise LiveExperimentError(
                "copied task repository does not match the bound template snapshot"
            )
        selected_workflow_ref = arm.get("config_ref")
        for workflow_ref in self.workflow_refs:
            if workflow_ref == selected_workflow_ref:
                continue
            other_workflow = _resolve_inside(
                workspace, workflow_ref, "unselected workflow config reference"
            )
            if other_workflow.is_file():
                other_workflow.unlink()
        for label, reference in (
            ("workflow config reference", selected_workflow_ref),
            ("specification reference", task.get("spec_ref")),
            ("evidence contract reference", self.config.task_bindings[task_id]),
        ):
            candidate = _resolve_inside(workspace, reference, label)
            if not candidate.is_file():
                raise LiveExperimentError(f"{label} does not exist in the task template")
        _initialize_workspace(workspace)

        status_root = _safe_direct_child_directory(self.batch_dir, "live-status")
        preflight_root = _safe_direct_child_directory(self.batch_dir, "live-preflight")
        status_path = status_root / f"{cell_id}.json"
        preflight_path = preflight_root / f"{cell_id}.json"
        if status_path.exists() or status_path.is_symlink():
            raise LiveExperimentError(f"live status already exists for cell: {cell_id}")
        if preflight_path.exists() or preflight_path.is_symlink():
            raise LiveExperimentError(f"live preflight already exists for cell: {cell_id}")
        _write_json(status_path, {"version": 1, "cell_id": cell_id, "status": "preflighting"})
        try:
            temporary_home = TemporaryCodexHome(self.source_codex_home)
            with temporary_home as clean_codex_home:
                prompt = CodexExperimentAdapter.render_prompt(arm, task, seed)
                preflight = run_codex_preflight(
                    policy=self.environment_policy,
                    command_prefix=self.command_prefix,
                    source_codex_home=temporary_home.source_home,
                    clean_codex_home=clean_codex_home,
                    workspace=workspace,
                    model=self.config.model,
                    rates=self.rates,
                    prompt=prompt,
                    today=self.preflight_date,
                )
                _write_json(preflight_path, preflight)
                _write_json(
                    status_path,
                    {"version": 1, "cell_id": cell_id, "status": "running"},
                )
                evidence_root = _safe_direct_child_directory(
                    self.batch_dir, "live-evidence"
                )
                runner = CodexExecRunner(
                    workspace_root=workspace_root,
                    evidence_root=evidence_root,
                    config=CodexExecConfig(
                        command_prefix=self.command_prefix,
                        sandbox=self.config.sandbox,
                        model=self.config.model,
                        codex_home=clean_codex_home,
                        approve_for_me=self.config.approval_mode == "auto-review",
                        timeout_seconds=self.config.timeout_seconds,
                    ),
                )
                adapter = CodexExperimentAdapter(
                    runner=runner,
                    workspace_resolver=lambda selected_arm, selected_task, selected_seed: workspace,
                    evaluator=EvidenceContractEvaluator(
                        self.config.task_bindings[task_id]
                    ),
                    cost_meter=JsonlUsageCostMeter(self.rates),
                )
                observation = adapter.run(arm, task, seed)
        except Exception as error:
            _write_json(
                status_path,
                {
                    "version": 1,
                    "cell_id": cell_id,
                    "status": "failed",
                    "error_type": type(error).__name__,
                },
            )
            raise

        _write_json(status_path, {"version": 1, "cell_id": cell_id, "status": "completed"})
        prefixed_refs = tuple(f"live-evidence/{ref}" for ref in observation.evidence_refs)
        return RunObservation(
            claimed_complete=observation.claimed_complete,
            verified_complete=observation.verified_complete,
            regressions=observation.regressions,
            cost=observation.cost,
            time_seconds=observation.time_seconds,
            human_interventions=observation.human_interventions,
            evidence_refs=tuple(
                dict.fromkeys(
                    (
                        *prefixed_refs,
                        preflight_path.relative_to(self.batch_dir).as_posix(),
                        status_path.relative_to(self.batch_dir).as_posix(),
                    )
                )
            ),
        )


def _load_rates(value: Mapping[str, Any]) -> UsageRates:
    if set(value) != RATE_FIELDS or value.get("version") != 1:
        raise LiveExperimentError("usage rate card must contain exactly the version 1 fields")
    return UsageRates.from_mapping(value)


def run_live_experiment(
    project_root: Path,
    config_path: Path,
    *,
    command_prefix: tuple[str, ...] = ("codex",),
    source_codex_home: Path | None = None,
    preflight_date: date | None = None,
) -> BatchOutcome:
    """Run or resume one bounded invocation of a live Codex experiment."""

    project_root = project_root.resolve()
    if not project_root.is_dir():
        raise LiveExperimentError("project root does not exist")
    config_path = config_path.resolve()
    try:
        config_path.relative_to(project_root)
    except ValueError as error:
        raise LiveExperimentError("live experiment config must be inside the project root") from error
    config_mapping = _load_object(config_path, "live experiment config")
    config = LiveExperimentConfig.from_mapping(config_mapping)
    if not command_prefix or any(not isinstance(part, str) or not part for part in command_prefix):
        raise LiveExperimentError("command prefix must contain non-empty strings")

    batch_mapping = _load_object(
        _resolve_inside(project_root, config.batch_ref, "batch reference"),
        "batch config",
    )
    batch = BatchExperimentConfig.from_mapping(batch_mapping)
    plan = _load_object(
        _resolve_inside(project_root, batch.experiment_ref, "experiment reference"),
        "experiment plan",
    )
    validate_experiment_plan(plan)
    rates_mapping = _load_object(
        _resolve_inside(project_root, config.rates_ref, "rate-card reference"),
        "usage rate card",
    )
    rates = _load_rates(rates_mapping)
    environment_mapping = _load_object(
        _resolve_inside(project_root, config.environment_ref, "environment-policy reference"),
        "Codex environment policy",
    )
    environment_policy = CodexEnvironmentPolicy.from_mapping(environment_mapping)
    executor_version = _probe_executor_version(
        command_prefix, project_root, environment_policy.preflight_timeout_seconds
    )
    if config.approval_mode == "auto-review":
        require_approve_for_me_support(
            command_prefix,
            cwd=project_root,
            timeout_seconds=environment_policy.preflight_timeout_seconds,
        )
    if rates.model != config.model:
        raise LiveExperimentError("rate-card model does not match live experiment model")
    if rates.unit != batch.cost_unit:
        raise LiveExperimentError("rate-card unit does not match the batch cost unit")
    if config.timeout_seconds > batch.maximum_time_per_run_seconds:
        raise LiveExperimentError("live timeout exceeds the batch per-run time ceiling")

    arm_ids = [plan["control"]["id"], *[arm["id"] for arm in plan["treatments"]]]
    if any(not ID_PATTERN.fullmatch(arm_id) for arm_id in arm_ids):
        raise LiveExperimentError("all live arm IDs must be path-safe")
    task_ids = [task["id"] for task in plan["tasks"]]
    if any(not ID_PATTERN.fullmatch(task_id) for task_id in task_ids):
        raise LiveExperimentError("all live task IDs must be path-safe")
    if set(task_ids) != set(config.task_bindings):
        raise LiveExperimentError("task bindings must exactly match experiment tasks")
    workflow_refs = tuple(
        arm["config_ref"] for arm in [plan["control"], *plan["treatments"]]
    )
    if len(workflow_refs) != len(set(workflow_refs)):
        raise LiveExperimentError("live experiment arms require distinct workflow configs")

    template_snapshots: dict[str, Mapping[str, Any]] = {}
    for task in plan["tasks"]:
        template = _resolve_inside(
            project_root, task["repository"], "task repository reference"
        )
        snapshot = _template_snapshot(template)
        for label, reference in (
            ("specification reference", task["spec_ref"]),
            ("evidence contract reference", config.task_bindings[task["id"]]),
        ):
            if not _resolve_inside(template, reference, label).is_file():
                raise LiveExperimentError(f"{label} does not exist in the task template")
        for arm in [plan["control"], *plan["treatments"]]:
            if not _resolve_inside(
                template, arm["config_ref"], "workflow config reference"
            ).is_file():
                raise LiveExperimentError(
                    "workflow config reference does not exist in the task template"
                )
        template_snapshots[task["id"]] = snapshot

    execution_fingerprint = _fingerprint(
        {
            "version": 1,
            "live_config": config_mapping,
            "rates": rates_mapping,
            "environment": environment_mapping,
            "templates": template_snapshots,
            "command_prefix": list(command_prefix),
            "executor_version": executor_version,
        }
    )
    run_root = _resolve_inside(project_root, batch.run_root_ref, "run-root reference")
    batch_dir = run_root / batch.batch_id
    adapter = LiveCodexBatchAdapter(
        project_root=project_root,
        batch_dir=batch_dir,
        config=config,
        rates=rates,
        environment_policy=environment_policy,
        template_snapshots=template_snapshots,
        workflow_refs=workflow_refs,
        command_prefix=command_prefix,
        source_codex_home=source_codex_home,
        preflight_date=preflight_date,
    )
    return run_experiment_batch(
        plan,
        {arm_id: adapter for arm_id in arm_ids},
        batch,
        run_root,
        execution_fingerprint=execution_fingerprint,
    )


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("config", type=Path)
    parser.add_argument("--project-root", type=Path, default=Path.cwd())
    parser.add_argument(
        "--confirm-paid-run",
        action="store_true",
        help="confirm that this invocation may execute paid or credit-using model cells",
    )
    arguments = parser.parse_args(argv)
    if not arguments.confirm_paid_run:
        raise LiveExperimentError("live execution requires --confirm-paid-run")
    root = arguments.project_root.resolve()
    outcome = run_live_experiment(root, arguments.config)
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
