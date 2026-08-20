"""Prepare and run one isolated, evidence-backed Codex control pilot."""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
from collections.abc import Mapping, Sequence
from datetime import date
from pathlib import Path
from typing import Any

from .active_spec import compile_history
from .codex_adapter import (
    SAFE_SANDBOXES,
    CodexAdapterError,
    CodexExecConfig,
    CodexExecRunner,
    CodexExperimentAdapter,
    require_approve_for_me_support,
)
from .codex_evidence import EvidenceContractEvaluator, JsonlUsageCostMeter, UsageRates
from .codex_environment import (
    CodexEnvironmentPolicy,
    TemporaryCodexHome,
    run_codex_preflight,
)


class LivePilotError(CodexAdapterError):
    """Raised when a live pilot cannot be prepared or trusted."""


ID_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")
CONFIG_FIELDS = {
    "version",
    "pilot_id",
    "template_ref",
    "run_root_ref",
    "arm",
    "task",
    "evidence_contract_ref",
    "rates_ref",
    "environment_ref",
    "model",
    "sandbox",
    "approval_mode",
    "timeout_seconds",
    "seed",
}
OPTIONAL_CONFIG_FIELDS = {"spec_history_ref"}
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


def _write_json(path: Path, value: Any) -> None:
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


def _load_object(path: Path, label: str) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        raise LivePilotError(f"{label} is not valid UTF-8 JSON: {path}") from error
    if not isinstance(value, dict):
        raise LivePilotError(f"{label} must be a JSON object")
    return value


def _resolve_inside(root: Path, reference: str, label: str) -> Path:
    if not isinstance(reference, str) or not reference:
        raise LivePilotError(f"{label} must be a non-empty relative path")
    path = Path(reference)
    if path.is_absolute():
        raise LivePilotError(f"{label} must be relative to the project root")
    root = root.resolve()
    candidate = (root / path).resolve()
    try:
        candidate.relative_to(root)
    except ValueError as error:
        raise LivePilotError(f"{label} escapes the project root: {reference}") from error
    return candidate


def _require_id(value: Any, label: str) -> str:
    if not isinstance(value, str) or not ID_PATTERN.fullmatch(value):
        raise LivePilotError(f"{label} must be a path-safe ID")
    return value


def _validate_config(config: Mapping[str, Any]) -> None:
    if not CONFIG_FIELDS <= set(config) or not set(config) <= (
        CONFIG_FIELDS | OPTIONAL_CONFIG_FIELDS
    ):
        missing = sorted(CONFIG_FIELDS - set(config))
        extra = sorted(set(config) - CONFIG_FIELDS - OPTIONAL_CONFIG_FIELDS)
        raise LivePilotError(f"pilot config fields do not match; missing={missing}, extra={extra}")
    if config["version"] != 1:
        raise LivePilotError("pilot config version must be 1")
    _require_id(config["pilot_id"], "pilot ID")
    arm = config["arm"]
    task = config["task"]
    if not isinstance(arm, Mapping) or set(arm) != {"id", "workflow", "config_ref"}:
        raise LivePilotError("arm must contain id, workflow, and config_ref")
    if not isinstance(task, Mapping) or set(task) != {"id", "repository", "spec_ref"}:
        raise LivePilotError("task must contain id, repository, and spec_ref")
    _require_id(arm["id"], "arm ID")
    _require_id(task["id"], "task ID")
    for label, value in (
        ("workflow", arm["workflow"]),
        ("workflow config reference", arm["config_ref"]),
        ("repository", task["repository"]),
        ("specification reference", task["spec_ref"]),
        ("model", config["model"]),
    ):
        if not isinstance(value, str) or not value:
            raise LivePilotError(f"{label} must be a non-empty string")
    if config["sandbox"] not in SAFE_SANDBOXES:
        raise LivePilotError("pilot sandbox must be read-only or workspace-write")
    if config["approval_mode"] not in {"none", "auto-review"}:
        raise LivePilotError("pilot approval mode must be none or auto-review")
    if (
        config["sandbox"] == "workspace-write"
        and config["approval_mode"] != "auto-review"
    ):
        raise LivePilotError("workspace-write pilots require auto-review")
    if config["sandbox"] == "read-only" and config["approval_mode"] != "none":
        raise LivePilotError("read-only pilots cannot enable auto-review")
    timeout = config["timeout_seconds"]
    if isinstance(timeout, bool) or not isinstance(timeout, (int, float)) or timeout <= 0:
        raise LivePilotError("pilot timeout must be a positive number")
    seed = config["seed"]
    if isinstance(seed, bool) or not isinstance(seed, int) or seed < 0:
        raise LivePilotError("pilot seed must be a non-negative integer")
    if "spec_history_ref" in config and (
        not isinstance(config["spec_history_ref"], str)
        or not config["spec_history_ref"]
    ):
        raise LivePilotError("specification history reference must be a non-empty string")


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
        detail = completed.stderr.strip() or completed.stdout.strip()
        raise LivePilotError(f"could not initialize pilot Git repository: {detail}")


def _initialize_workspace(workspace: Path) -> None:
    _run_git(workspace, "init", "--quiet")
    _run_git(workspace, "add", "--all")
    _run_git(
        workspace,
        "-c",
        "user.name=Agentic Engineering Pilot",
        "-c",
        "user.email=pilot@agentic-engineering.invalid",
        "commit",
        "--quiet",
        "-m",
        "Seed isolated pilot fixture",
    )


def _reject_template_links(template: Path) -> None:
    def is_link(path: Path) -> bool:
        is_junction = getattr(path, "is_junction", lambda: False)
        return path.is_symlink() or is_junction()

    if is_link(template) or any(is_link(path) for path in template.rglob("*")):
        raise LivePilotError("pilot templates may not contain filesystem links")


def run_live_pilot(
    project_root: Path,
    config_path: Path,
    run_id: str,
    *,
    command_prefix: tuple[str, ...] = ("codex",),
    source_codex_home: Path | None = None,
    preflight_date: date | None = None,
) -> dict[str, Any]:
    """Run exactly one fresh control cell and return its private summary."""

    project_root = project_root.resolve()
    if not project_root.is_dir():
        raise LivePilotError("project root does not exist")
    _require_id(run_id, "run ID")
    config_path = config_path.resolve()
    try:
        config_path.relative_to(project_root)
    except ValueError as error:
        raise LivePilotError("pilot config must be inside the project root") from error
    config = _load_object(config_path, "pilot config")
    _validate_config(config)

    template = _resolve_inside(project_root, config["template_ref"], "template reference")
    rates_path = _resolve_inside(project_root, config["rates_ref"], "rate-card reference")
    environment_path = _resolve_inside(
        project_root, config["environment_ref"], "environment-policy reference"
    )
    history_path = None
    if "spec_history_ref" in config:
        history_path = _resolve_inside(
            project_root, config["spec_history_ref"], "specification history reference"
        )
        if not history_path.is_file():
            raise LivePilotError("specification history reference does not exist")
    run_root = _resolve_inside(project_root, config["run_root_ref"], "run-root reference")
    if not template.is_dir():
        raise LivePilotError(f"pilot template does not exist: {template}")
    _reject_template_links(template)
    rate_card = _load_object(rates_path, "usage rate card")
    if set(rate_card) != RATE_FIELDS or rate_card.get("version") != 1:
        raise LivePilotError("usage rate card must contain exactly the version 1 fields")
    rates = UsageRates.from_mapping(rate_card)
    environment_policy = CodexEnvironmentPolicy.from_mapping(
        _load_object(environment_path, "Codex environment policy")
    )
    if config["approval_mode"] == "auto-review":
        require_approve_for_me_support(
            command_prefix,
            cwd=project_root,
            timeout_seconds=environment_policy.preflight_timeout_seconds,
        )

    run_dir = run_root / run_id
    if run_dir.exists():
        raise LivePilotError(f"pilot run already exists and will not be overwritten: {run_id}")
    workspace_root = run_dir / "workspaces"
    workspace = workspace_root / config["task"]["id"]
    evidence_root = run_dir / "evidence"
    workspace.parent.mkdir(parents=True, exist_ok=False)
    shutil.copytree(template, workspace)
    if history_path is not None:
        history = _load_object(history_path, "specification history")
        try:
            active_spec = compile_history(history)
        except (TypeError, ValueError) as error:
            raise LivePilotError(f"could not compile specification history: {error}") from error
        spec_path = _resolve_inside(
            workspace, config["task"]["spec_ref"], "specification reference"
        )
        spec_path.parent.mkdir(parents=True, exist_ok=True)
        _write_json(spec_path, active_spec)
    for label, reference in (
        ("workflow config reference", config["arm"]["config_ref"]),
        ("specification reference", config["task"]["spec_ref"]),
        ("evidence contract reference", config["evidence_contract_ref"]),
    ):
        candidate = _resolve_inside(workspace, reference, label)
        if not candidate.is_file():
            raise LivePilotError(f"{label} does not exist in the pilot template")
    _initialize_workspace(workspace)

    status_path = run_dir / "pilot-status.json"
    _write_json(
        status_path,
        {
            "version": 1,
            "pilot_id": config["pilot_id"],
            "run_id": run_id,
            "status": "preflighting",
        },
    )
    try:
        temporary_home = TemporaryCodexHome(source_codex_home)
        with temporary_home as clean_codex_home:
            prompt = CodexExperimentAdapter.render_prompt(
                config["arm"], config["task"], config["seed"]
            )
            preflight = run_codex_preflight(
                policy=environment_policy,
                command_prefix=command_prefix,
                source_codex_home=temporary_home.source_home,
                clean_codex_home=clean_codex_home,
                workspace=workspace,
                model=config["model"],
                rates=rates,
                prompt=prompt,
                today=preflight_date,
            )
            _write_json(run_dir / "preflight-report.json", preflight)
            _write_json(
                status_path,
                {
                    "version": 1,
                    "pilot_id": config["pilot_id"],
                    "run_id": run_id,
                    "status": "running",
                },
            )
            runner = CodexExecRunner(
                workspace_root=workspace_root,
                evidence_root=evidence_root,
                config=CodexExecConfig(
                    command_prefix=command_prefix,
                    sandbox=config["sandbox"],
                    model=config["model"],
                    codex_home=clean_codex_home,
                    approve_for_me=config["approval_mode"] == "auto-review",
                    timeout_seconds=float(config["timeout_seconds"]),
                ),
            )
            adapter = CodexExperimentAdapter(
                runner=runner,
                workspace_resolver=lambda arm, task, seed: workspace,
                evaluator=EvidenceContractEvaluator(config["evidence_contract_ref"]),
                cost_meter=JsonlUsageCostMeter(rates),
            )
            observation = adapter.run(config["arm"], config["task"], config["seed"])
    except Exception as error:
        _write_json(
            status_path,
            {
                "version": 1,
                "pilot_id": config["pilot_id"],
                "run_id": run_id,
                "status": "failed",
                "error_type": type(error).__name__,
                "error": str(error),
            },
        )
        raise

    summary = {
        "version": 1,
        "pilot_id": config["pilot_id"],
        "run_id": run_id,
        "arm_id": config["arm"]["id"],
        "task_id": config["task"]["id"],
        "seed": config["seed"],
        "model": config["model"],
        "sandbox": config["sandbox"],
        "approval_mode": config["approval_mode"],
        "claimed_complete": observation.claimed_complete,
        "verified_complete": observation.verified_complete,
        "regressions": observation.regressions,
        "measured_cost": observation.cost,
        "cost_unit": rates.unit,
        "rate_effective_date": rates.effective_date,
        "rate_source_url": rates.source_url,
        "preflight_ref": "preflight-report.json",
        "preflight_prompt_json_bytes": preflight["prompt_json_bytes"],
        "preflight_enabled_plugin_count": preflight["enabled_plugin_count"],
        "preflight_enabled_mcp_count": preflight["enabled_mcp_count"],
        "time_seconds": observation.time_seconds,
        "human_interventions": observation.human_interventions,
        "evidence_refs": list(observation.evidence_refs),
    }
    _write_json(run_dir / "pilot-summary.json", summary)
    _write_json(
        status_path,
        {"version": 1, "pilot_id": config["pilot_id"], "run_id": run_id, "status": "completed"},
    )
    return summary


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("config", type=Path)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--project-root", type=Path, default=Path.cwd())
    arguments = parser.parse_args(argv)
    summary = run_live_pilot(
        arguments.project_root, arguments.config, arguments.run_id
    )
    json.dump(summary, sys.stdout, ensure_ascii=False, indent=2)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
