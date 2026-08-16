"""Safe Codex CLI execution adapter for controlled workflow experiments."""

from __future__ import annotations

import hashlib
import json
import math
import os
import re
import shutil
import subprocess
import time
from collections.abc import Callable, Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Protocol

from .experiments import RunObservation


class CodexAdapterError(RuntimeError):
    """Raised when a Codex experiment cell cannot produce trustworthy evidence."""


SAFE_SANDBOXES = {"read-only", "workspace-write"}
ID_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")
SUBMISSION_SCHEMA: dict[str, Any] = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "type": "object",
    "additionalProperties": False,
    "required": ["claimed_complete", "summary", "artifact_refs"],
    "properties": {
        "claimed_complete": {"type": "boolean"},
        "summary": {"type": "string", "minLength": 1},
        "artifact_refs": {
            "type": "array",
            "items": {"type": "string", "minLength": 1},
        },
    },
}


@dataclass(frozen=True)
class CodexExecConfig:
    """Trusted host configuration for one Codex CLI adapter."""

    command_prefix: tuple[str, ...] = ("codex",)
    sandbox: str = "workspace-write"
    model: str | None = None
    profile: str | None = None
    codex_home: Path | None = None
    approve_for_me: bool = False
    timeout_seconds: float = 1800.0

    def __post_init__(self) -> None:
        if not self.command_prefix or any(
            not isinstance(part, str) or not part for part in self.command_prefix
        ):
            raise CodexAdapterError("command prefix must contain non-empty strings")
        if self.sandbox not in SAFE_SANDBOXES:
            raise CodexAdapterError(
                "sandbox must be read-only or workspace-write; unrestricted modes are refused"
            )
        if not isinstance(self.approve_for_me, bool):
            raise CodexAdapterError("approve_for_me must be a boolean")
        if self.approve_for_me and self.sandbox != "workspace-write":
            raise CodexAdapterError(
                "approve_for_me requires the workspace-write sandbox"
            )
        if (
            isinstance(self.timeout_seconds, bool)
            or not isinstance(self.timeout_seconds, (int, float))
            or not math.isfinite(self.timeout_seconds)
            or self.timeout_seconds <= 0
        ):
            raise CodexAdapterError("timeout must be a positive finite number")
        for label, value in (("model", self.model), ("profile", self.profile)):
            if value is not None and (not isinstance(value, str) or not value):
                raise CodexAdapterError(f"{label} must be a non-empty string when set")
        if self.codex_home is not None:
            if not isinstance(self.codex_home, Path) or not self.codex_home.is_absolute():
                raise CodexAdapterError("Codex home must be an absolute path when set")
            if not self.codex_home.is_dir():
                raise CodexAdapterError("configured Codex home does not exist")


@dataclass(frozen=True)
class CodexSubmission:
    """Untrusted completion claim returned by the executor."""

    claimed_complete: bool
    summary: str
    artifact_refs: tuple[str, ...]


@dataclass(frozen=True)
class CodexRunResult:
    """Captured executor output and persisted evidence for one cell."""

    submission: CodexSubmission
    model: str | None
    duration_seconds: float
    stdout: str
    stderr: str
    evidence_dir: Path
    evidence_refs: tuple[str, ...]


@dataclass(frozen=True)
class EvaluationOutcome:
    """Independent result that, unlike the submission, may verify completion."""

    verified_complete: bool
    regressions: int
    evidence_refs: tuple[str, ...]


@dataclass(frozen=True)
class CostMeasurement:
    """Externally derived cost plus evidence explaining the measurement."""

    cost: float
    evidence_refs: tuple[str, ...]


class IndependentEvaluator(Protocol):
    """Evaluate a completed workspace without trusting the executor's claim."""

    def evaluate(
        self,
        workspace: Path,
        task: Mapping[str, Any],
        submission: CodexSubmission,
        evidence_dir: Path,
    ) -> EvaluationOutcome: ...


class CostMeter(Protocol):
    """Measure externally sourced run cost."""

    def measure(
        self,
        result: CodexRunResult,
        arm: Mapping[str, Any],
        task: Mapping[str, Any],
        seed: int,
    ) -> float | CostMeasurement: ...


WorkspaceResolver = Callable[[Mapping[str, Any], Mapping[str, Any], int], Path]
Clock = Callable[[], float]
ExecutableResolver = Callable[[str], str | None]


def resolve_command_prefix(
    command_prefix: tuple[str, ...],
    *,
    platform_name: str = os.name,
    resolver: ExecutableResolver = shutil.which,
) -> tuple[str, ...]:
    """Resolve the Windows Codex batch shim without enabling shell execution."""

    if platform_name != "nt" or command_prefix[0].casefold() != "codex":
        return command_prefix
    for candidate in ("codex.cmd", "codex.exe"):
        resolved = resolver(candidate)
        if resolved:
            return (resolved, *command_prefix[1:])
    return command_prefix


def require_approve_for_me_support(
    command_prefix: tuple[str, ...],
    *,
    cwd: Path,
    timeout_seconds: float,
) -> None:
    """Fail before model execution when the CLI cannot route approvals to auto-review."""

    try:
        completed = subprocess.run(
            [*resolve_command_prefix(command_prefix), "exec", "--help"],
            cwd=cwd,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            shell=False,
            timeout=timeout_seconds,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired) as error:
        raise CodexAdapterError(
            "could not inspect Codex auto-review support"
        ) from error
    help_text = completed.stdout + completed.stderr
    if completed.returncode != 0 or "--approve-for-me" not in help_text:
        raise CodexAdapterError(
            "installed Codex CLI does not support --approve-for-me"
        )


def _resolve_inside(root: Path, candidate: Path, label: str) -> Path:
    root = root.resolve()
    candidate = candidate.resolve()
    try:
        candidate.relative_to(root)
    except ValueError as error:
        raise CodexAdapterError(f"{label} escapes configured root: {candidate}") from error
    return candidate


def _cell_id(arm_id: str, task_id: str, seed: int) -> str:
    if not ID_PATTERN.fullmatch(arm_id) or not ID_PATTERN.fullmatch(task_id):
        raise CodexAdapterError("arm and task IDs must be path-safe experiment IDs")
    if isinstance(seed, bool) or not isinstance(seed, int) or seed < 0:
        raise CodexAdapterError("seed must be a non-negative integer")
    return f"a-{arm_id}__t-{task_id}__s-{seed}"


def _write_json(path: Path, value: Any) -> None:
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


def _parse_submission(path: Path) -> CodexSubmission:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        raise CodexAdapterError("Codex did not produce a valid JSON submission") from error
    if not isinstance(value, Mapping) or set(value) != {
        "claimed_complete",
        "summary",
        "artifact_refs",
    }:
        raise CodexAdapterError("Codex submission does not match the required fields")
    claimed = value["claimed_complete"]
    summary = value["summary"]
    refs = value["artifact_refs"]
    if not isinstance(claimed, bool):
        raise CodexAdapterError("claimed_complete must be a boolean")
    if not isinstance(summary, str) or not summary.strip():
        raise CodexAdapterError("submission summary must be a non-empty string")
    if not isinstance(refs, list) or any(
        not isinstance(ref, str) or not ref for ref in refs
    ):
        raise CodexAdapterError("artifact_refs must be an array of non-empty strings")
    if len(refs) != len(set(refs)):
        raise CodexAdapterError("artifact_refs must be unique")
    return CodexSubmission(claimed, summary, tuple(refs))


class CodexExecRunner:
    """Run `codex exec` with stdin prompts and persist raw executor evidence."""

    def __init__(
        self,
        workspace_root: Path,
        evidence_root: Path,
        config: CodexExecConfig | None = None,
        clock: Clock = time.monotonic,
    ):
        self.workspace_root = workspace_root.resolve()
        self.evidence_root = evidence_root.resolve()
        self.config = config or CodexExecConfig()
        self.clock = clock

    def execute(
        self,
        *,
        arm_id: str,
        task_id: str,
        seed: int,
        workspace: Path,
        prompt: str,
    ) -> CodexRunResult:
        if not self.workspace_root.is_dir():
            raise CodexAdapterError("configured workspace root does not exist")
        workspace = _resolve_inside(self.workspace_root, workspace, "workspace")
        if not workspace.is_dir():
            raise CodexAdapterError(f"workspace does not exist: {workspace}")
        if not isinstance(prompt, str) or not prompt.strip():
            raise CodexAdapterError("prompt must be a non-empty string")

        cell_id = _cell_id(arm_id, task_id, seed)
        self.evidence_root.mkdir(parents=True, exist_ok=True)
        evidence_dir = _resolve_inside(
            self.evidence_root, self.evidence_root / cell_id, "evidence directory"
        )
        try:
            evidence_dir.mkdir()
        except FileExistsError as error:
            raise CodexAdapterError(f"evidence already exists for cell: {cell_id}") from error

        schema_path = evidence_dir / "submission-schema.json"
        final_path = evidence_dir / "final-message.json"
        stdout_path = evidence_dir / "stdout.txt"
        stderr_path = evidence_dir / "stderr.txt"
        request_path = evidence_dir / "request.json"
        process_path = evidence_dir / "process.json"
        _write_json(schema_path, SUBMISSION_SCHEMA)

        command = [
            *resolve_command_prefix(self.config.command_prefix),
            "exec",
            "--ephemeral",
            "--color",
            "never",
            "--json",
            "--sandbox",
            self.config.sandbox,
        ]
        if self.config.approve_for_me:
            command.append("--approve-for-me")
        command.extend(
            [
                "-C",
                str(workspace),
                "--output-schema",
                str(schema_path),
                "--output-last-message",
                str(final_path),
            ]
        )
        if self.config.model:
            command.extend(["--model", self.config.model])
        if self.config.profile:
            command.extend(["--profile", self.config.profile])
        command.append("-")
        request = {
            "version": 1,
            "cell_id": cell_id,
            "arm_id": arm_id,
            "task_id": task_id,
            "seed": seed,
            "workspace": str(workspace),
            "sandbox": self.config.sandbox,
            "approval_mode": (
                "auto-review" if self.config.approve_for_me else "none"
            ),
            "model": self.config.model,
            "profile": self.config.profile,
            "isolated_codex_home": self.config.codex_home is not None,
            "timeout_seconds": self.config.timeout_seconds,
            "prompt_sha256": hashlib.sha256(prompt.encode("utf-8")).hexdigest(),
        }
        _write_json(request_path, request)

        started = self.clock()
        try:
            environment = os.environ.copy()
            if self.config.codex_home is not None:
                environment["CODEX_HOME"] = str(self.config.codex_home)
            completed = subprocess.run(
                command,
                cwd=workspace,
                env=environment,
                input=prompt,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                shell=False,
                timeout=self.config.timeout_seconds,
                check=False,
            )
        except subprocess.TimeoutExpired as error:
            stdout = error.stdout if isinstance(error.stdout, str) else ""
            stderr = error.stderr if isinstance(error.stderr, str) else ""
            stdout_path.write_text(stdout, encoding="utf-8")
            stderr_path.write_text(stderr, encoding="utf-8")
            _write_json(
                process_path,
                {"version": 1, "outcome": "timeout", "return_code": None},
            )
            raise CodexAdapterError(
                f"Codex timed out after {self.config.timeout_seconds} seconds"
            ) from error
        except OSError as error:
            _write_json(
                process_path,
                {"version": 1, "outcome": "start_error", "return_code": None},
            )
            raise CodexAdapterError(f"Codex could not start: {error}") from error
        duration = self.clock() - started
        stdout_path.write_text(completed.stdout, encoding="utf-8")
        stderr_path.write_text(completed.stderr, encoding="utf-8")
        _write_json(
            process_path,
            {
                "version": 1,
                "outcome": "exited",
                "return_code": completed.returncode,
                "duration_seconds": duration,
            },
        )
        if completed.returncode != 0:
            raise CodexAdapterError(
                f"Codex exited with code {completed.returncode}; raw output was preserved"
            )

        submission = _parse_submission(final_path)
        refs = tuple(
            path.relative_to(self.evidence_root).as_posix()
            for path in (
                request_path,
                process_path,
                schema_path,
                final_path,
                stdout_path,
                stderr_path,
            )
        )
        return CodexRunResult(
            submission=submission,
            model=self.config.model,
            duration_seconds=duration,
            stdout=completed.stdout,
            stderr=completed.stderr,
            evidence_dir=evidence_dir,
            evidence_refs=refs,
        )


class CodexExperimentAdapter:
    """Convert one isolated Codex execution plus independent checks into M06 evidence."""

    def __init__(
        self,
        runner: CodexExecRunner,
        workspace_resolver: WorkspaceResolver,
        evaluator: IndependentEvaluator,
        cost_meter: CostMeter,
    ):
        self.runner = runner
        self.workspace_resolver = workspace_resolver
        self.evaluator = evaluator
        self.cost_meter = cost_meter

    def run(
        self, arm: Mapping[str, Any], task: Mapping[str, Any], seed: int
    ) -> RunObservation:
        arm_id = arm.get("id")
        task_id = task.get("id")
        if not isinstance(arm_id, str) or not isinstance(task_id, str):
            raise CodexAdapterError("arm and task require string IDs")
        workspace = self.workspace_resolver(arm, task, seed)
        prompt = self.render_prompt(arm, task, seed)
        result = self.runner.execute(
            arm_id=arm_id,
            task_id=task_id,
            seed=seed,
            workspace=workspace,
            prompt=prompt,
        )
        outcome = self.evaluator.evaluate(
            workspace.resolve(), task, result.submission, result.evidence_dir
        )
        self._validate_outcome(outcome)
        measurement = self.cost_meter.measure(result, arm, task, seed)
        cost_evidence_refs: tuple[str, ...] = ()
        if isinstance(measurement, CostMeasurement):
            cost = measurement.cost
            cost_evidence_refs = measurement.evidence_refs
            if not cost_evidence_refs or any(
                not isinstance(ref, str) or not ref for ref in cost_evidence_refs
            ):
                raise CodexAdapterError("cost measurement requires evidence references")
            if len(cost_evidence_refs) != len(set(cost_evidence_refs)):
                raise CodexAdapterError("cost evidence references must be unique")
        else:
            cost = measurement
        if isinstance(cost, bool) or not isinstance(cost, (int, float)):
            raise CodexAdapterError("cost meter must return a non-negative finite number")
        if not math.isfinite(cost) or cost < 0:
            raise CodexAdapterError("cost meter must return a non-negative finite number")

        evaluation_path = result.evidence_dir / "independent-evaluation.json"
        _write_json(
            evaluation_path,
            {
                "version": 1,
                "verified_complete": outcome.verified_complete,
                "regressions": outcome.regressions,
                "evidence_refs": list(outcome.evidence_refs),
            },
        )
        evaluation_ref = evaluation_path.relative_to(
            self.runner.evidence_root
        ).as_posix()
        evidence_refs = tuple(
            dict.fromkeys(
                (
                    *result.evidence_refs,
                    evaluation_ref,
                    *outcome.evidence_refs,
                    *cost_evidence_refs,
                )
            )
        )
        return RunObservation(
            claimed_complete=result.submission.claimed_complete,
            verified_complete=outcome.verified_complete,
            regressions=outcome.regressions,
            cost=float(cost),
            time_seconds=result.duration_seconds,
            human_interventions=0,
            evidence_refs=evidence_refs,
        )

    @staticmethod
    def render_prompt(
        arm: Mapping[str, Any], task: Mapping[str, Any], seed: int
    ) -> str:
        return (
            "Execute one bounded agentic-engineering experiment cell.\n"
            f"Task ID: {task.get('id')}\n"
            f"Specification reference: {task.get('spec_ref')}\n"
            f"Workflow: {arm.get('workflow')}\n"
            f"Workflow configuration reference: {arm.get('config_ref')}\n"
            f"Trial seed label: {seed}\n\n"
            "Work only in the current repository workspace. Read the specification and "
            "workflow configuration, implement the bounded task, and run relevant checks. "
            "Return the required structured submission. Your completion claim is advisory; "
            "an independent evaluator decides whether the task is verified."
        )

    @staticmethod
    def _validate_outcome(outcome: EvaluationOutcome) -> None:
        if not isinstance(outcome, EvaluationOutcome):
            raise CodexAdapterError("independent evaluator returned an invalid outcome")
        if not isinstance(outcome.verified_complete, bool):
            raise CodexAdapterError("verified_complete must be a boolean")
        if (
            isinstance(outcome.regressions, bool)
            or not isinstance(outcome.regressions, int)
            or outcome.regressions < 0
        ):
            raise CodexAdapterError("regressions must be a non-negative integer")
        if outcome.verified_complete and outcome.regressions:
            raise CodexAdapterError("verified completion cannot contain regressions")
        if not outcome.evidence_refs or any(
            not isinstance(ref, str) or not ref for ref in outcome.evidence_refs
        ):
            raise CodexAdapterError("independent evaluation requires evidence references")
        if len(outcome.evidence_refs) != len(set(outcome.evidence_refs)):
            raise CodexAdapterError("independent evidence references must be unique")
