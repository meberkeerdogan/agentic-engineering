"""Concrete independent-evaluation and usage-cost bridges for Codex runs."""

from __future__ import annotations

import json
import math
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .codex_adapter import (
    CodexAdapterError,
    CodexRunResult,
    CodexSubmission,
    CostMeasurement,
    EvaluationOutcome,
)
from .evaluators import run_single_pass_baseline


class CodexEvidenceError(CodexAdapterError):
    """Raised when independent evidence or metering cannot be derived safely."""


def _resolve_inside(root: Path, relative_path: str, label: str) -> Path:
    if not isinstance(relative_path, str) or not relative_path:
        raise CodexEvidenceError(f"{label} must be a non-empty relative path")
    path = Path(relative_path)
    if path.is_absolute():
        raise CodexEvidenceError(f"{label} must be relative to the workspace")
    root = root.resolve()
    candidate = (root / path).resolve()
    try:
        candidate.relative_to(root)
    except ValueError as error:
        raise CodexEvidenceError(f"{label} escapes the workspace: {relative_path}") from error
    return candidate


def _write_json(path: Path, value: Any) -> None:
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


class EvidenceContractEvaluator:
    """Run an existing read-only evidence contract after the executor finishes."""

    def __init__(self, contract_ref: str):
        self.contract_ref = contract_ref

    def evaluate(
        self,
        workspace: Path,
        task: Mapping[str, Any],
        submission: CodexSubmission,
        evidence_dir: Path,
    ) -> EvaluationOutcome:
        del task, submission
        contract_path = _resolve_inside(
            workspace, self.contract_ref, "evidence contract reference"
        )
        if not contract_path.is_file():
            raise CodexEvidenceError(
                f"evidence contract does not exist: {self.contract_ref}"
            )
        try:
            contract = json.loads(contract_path.read_text(encoding="utf-8"))
        except (OSError, UnicodeError, json.JSONDecodeError) as error:
            raise CodexEvidenceError("evidence contract is not valid UTF-8 JSON") from error
        if not isinstance(contract, Mapping):
            raise CodexEvidenceError("evidence contract must be a JSON object")

        report = run_single_pass_baseline(contract, workspace)
        report_path = evidence_dir / "evaluation-report.json"
        _write_json(report_path, report)
        report_ref = report_path.relative_to(evidence_dir.parent).as_posix()
        return EvaluationOutcome(
            verified_complete=report["outcome"] == "pass",
            regressions=len(report["regressions"]),
            evidence_refs=(report_ref,),
        )


@dataclass(frozen=True)
class UsageRates:
    """A dated, externally declared rate card for one model and cost unit."""

    model: str
    unit: str
    effective_date: str
    source_url: str
    input_per_million: float
    cached_input_per_million: float
    output_per_million: float

    def __post_init__(self) -> None:
        for label, value in (
            ("model", self.model),
            ("unit", self.unit),
            ("effective date", self.effective_date),
            ("source URL", self.source_url),
        ):
            if not isinstance(value, str) or not value:
                raise CodexEvidenceError(f"{label} must be a non-empty string")
        for label, value in (
            ("input rate", self.input_per_million),
            ("cached-input rate", self.cached_input_per_million),
            ("output rate", self.output_per_million),
        ):
            if isinstance(value, bool) or not isinstance(value, (int, float)):
                raise CodexEvidenceError(f"{label} must be non-negative and finite")
            if not math.isfinite(value) or value < 0:
                raise CodexEvidenceError(f"{label} must be non-negative and finite")

    @classmethod
    def from_mapping(cls, value: Mapping[str, Any]) -> UsageRates:
        try:
            return cls(
                model=value["model"],
                unit=value["unit"],
                effective_date=value["effective_date"],
                source_url=value["source_url"],
                input_per_million=value["input_per_million"],
                cached_input_per_million=value["cached_input_per_million"],
                output_per_million=value["output_per_million"],
            )
        except KeyError as error:
            raise CodexEvidenceError(f"rate card is missing field: {error.args[0]}") from error


USAGE_FIELDS = (
    "input_tokens",
    "cached_input_tokens",
    "output_tokens",
    "reasoning_output_tokens",
)


def parse_jsonl_usage(stdout: str) -> dict[str, int]:
    """Sum documented `turn.completed` usage events from Codex JSONL output."""

    totals = {field: 0 for field in USAGE_FIELDS}
    turn_count = 0
    for line_number, raw_line in enumerate(stdout.splitlines(), start=1):
        if not raw_line.strip():
            continue
        try:
            event = json.loads(raw_line)
        except json.JSONDecodeError as error:
            raise CodexEvidenceError(
                f"Codex JSONL line {line_number} is not valid JSON"
            ) from error
        if not isinstance(event, Mapping):
            raise CodexEvidenceError(
                f"Codex JSONL line {line_number} must contain an object"
            )
        if event.get("type") != "turn.completed":
            continue
        usage = event.get("usage")
        if not isinstance(usage, Mapping):
            raise CodexEvidenceError("turn.completed event is missing usage")
        values: dict[str, int] = {}
        for field in USAGE_FIELDS:
            value = usage.get(field)
            if isinstance(value, bool) or not isinstance(value, int) or value < 0:
                raise CodexEvidenceError(f"usage field {field} must be a non-negative integer")
            values[field] = value
        if values["cached_input_tokens"] > values["input_tokens"]:
            raise CodexEvidenceError("cached input tokens cannot exceed total input tokens")
        for field, value in values.items():
            totals[field] += value
        turn_count += 1
    if not turn_count:
        raise CodexEvidenceError("Codex JSONL contains no completed-turn usage")
    if totals["cached_input_tokens"] > totals["input_tokens"]:
        raise CodexEvidenceError("cached input tokens cannot exceed total input tokens")
    return {"turn_count": turn_count, **totals}


class JsonlUsageCostMeter:
    """Price documented Codex token usage with an explicit external rate card."""

    def __init__(self, rates: UsageRates):
        self.rates = rates

    def measure(
        self,
        result: CodexRunResult,
        arm: Mapping[str, Any],
        task: Mapping[str, Any],
        seed: int,
    ) -> CostMeasurement:
        del arm, task, seed
        if result.model is None:
            raise CodexEvidenceError(
                "usage pricing requires an explicit model in CodexExecConfig"
            )
        if result.model != self.rates.model:
            raise CodexEvidenceError(
                f"rate-card model {self.rates.model!r} does not match run model {result.model!r}"
            )
        usage = parse_jsonl_usage(result.stdout)
        uncached_input = usage["input_tokens"] - usage["cached_input_tokens"]
        cost = round(
            (
                uncached_input * self.rates.input_per_million
                + usage["cached_input_tokens"] * self.rates.cached_input_per_million
                + usage["output_tokens"] * self.rates.output_per_million
            )
            / 1_000_000,
            12,
        )
        if not math.isfinite(cost):
            raise CodexEvidenceError("measured usage cost is not finite")
        record = {
            "version": 1,
            "source": "codex-jsonl-turn.completed",
            "model": self.rates.model,
            "unit": self.rates.unit,
            "effective_date": self.rates.effective_date,
            "source_url": self.rates.source_url,
            "rates_per_million_tokens": {
                "input": self.rates.input_per_million,
                "cached_input": self.rates.cached_input_per_million,
                "output": self.rates.output_per_million,
            },
            "usage": usage,
            "uncached_input_tokens": uncached_input,
            "measured_cost": cost,
        }
        usage_path = result.evidence_dir / "usage-cost.json"
        _write_json(usage_path, record)
        usage_ref = usage_path.relative_to(result.evidence_dir.parent).as_posix()
        return CostMeasurement(cost=cost, evidence_refs=(usage_ref,))
