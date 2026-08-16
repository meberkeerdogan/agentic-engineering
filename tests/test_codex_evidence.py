import json
import shutil
from pathlib import Path

import pytest

from agentic_engineering.codex_adapter import CodexRunResult, CodexSubmission
from agentic_engineering.codex_evidence import (
    CodexEvidenceError,
    EvidenceContractEvaluator,
    JsonlUsageCostMeter,
    UsageRates,
    parse_jsonl_usage,
)

ROOT = Path(__file__).resolve().parents[1]


def copied_fixture(tmp_path: Path) -> Path:
    workspace = tmp_path / "workspace"
    shutil.copytree(ROOT / "examples" / "fixture-task", workspace)
    return workspace


def submission() -> CodexSubmission:
    return CodexSubmission(True, "executor says complete", ("solution.json",))


def test_evidence_contract_is_the_only_source_of_verified_completion(
    tmp_path: Path,
) -> None:
    workspace = copied_fixture(tmp_path)
    evidence_dir = tmp_path / "evidence" / "cell-1"
    evidence_dir.mkdir(parents=True)
    evaluator = EvidenceContractEvaluator("evidence-contract.json")

    outcome = evaluator.evaluate(workspace, {}, submission(), evidence_dir)

    report = json.loads((evidence_dir / "evaluation-report.json").read_text("utf-8"))
    assert outcome.verified_complete is True
    assert outcome.regressions == 0
    assert outcome.evidence_refs == ("cell-1/evaluation-report.json",)
    assert report["outcome"] == "pass"


def test_executor_claim_does_not_override_a_failed_contract(tmp_path: Path) -> None:
    workspace = copied_fixture(tmp_path)
    solution_path = workspace / "solution.json"
    solution = json.loads(solution_path.read_text("utf-8"))
    solution["status"] = "incomplete"
    solution_path.write_text(json.dumps(solution), encoding="utf-8")
    evidence_dir = tmp_path / "evidence" / "cell-1"
    evidence_dir.mkdir(parents=True)

    outcome = EvidenceContractEvaluator("evidence-contract.json").evaluate(
        workspace, {}, submission(), evidence_dir
    )

    assert outcome.verified_complete is False
    assert outcome.regressions == 3


def test_evidence_contract_cannot_escape_workspace(tmp_path: Path) -> None:
    workspace = copied_fixture(tmp_path)
    evidence_dir = tmp_path / "evidence" / "cell-1"
    evidence_dir.mkdir(parents=True)

    with pytest.raises(CodexEvidenceError, match="escapes the workspace"):
        EvidenceContractEvaluator("../contract.json").evaluate(
            workspace, {}, submission(), evidence_dir
        )


def test_missing_evidence_contract_fails_closed(tmp_path: Path) -> None:
    workspace = copied_fixture(tmp_path)
    evidence_dir = tmp_path / "evidence" / "cell-1"
    evidence_dir.mkdir(parents=True)

    with pytest.raises(CodexEvidenceError, match="does not exist"):
        EvidenceContractEvaluator("missing.json").evaluate(
            workspace, {}, submission(), evidence_dir
        )


def test_malformed_evidence_contract_fails_closed(tmp_path: Path) -> None:
    workspace = copied_fixture(tmp_path)
    (workspace / "broken-contract.json").write_text("not-json", encoding="utf-8")
    evidence_dir = tmp_path / "evidence" / "cell-1"
    evidence_dir.mkdir(parents=True)

    with pytest.raises(CodexEvidenceError, match="not valid UTF-8 JSON"):
        EvidenceContractEvaluator("broken-contract.json").evaluate(
            workspace, {}, submission(), evidence_dir
        )


def rates() -> UsageRates:
    return UsageRates(
        model="fixture-model",
        unit="credits",
        effective_date="2026-08-16",
        source_url="https://learn.chatgpt.com/docs/pricing",
        input_per_million=5.0,
        cached_input_per_million=0.5,
        output_per_million=30.0,
    )


def test_rate_card_requires_every_declared_field() -> None:
    with pytest.raises(CodexEvidenceError, match="missing field: output_per_million"):
        UsageRates.from_mapping(
            {
                "model": "fixture-model",
                "unit": "credits",
                "effective_date": "2026-08-16",
                "source_url": "https://learn.chatgpt.com/docs/pricing",
                "input_per_million": 5.0,
                "cached_input_per_million": 0.5,
            }
        )


def test_rate_card_rejects_negative_rates() -> None:
    with pytest.raises(CodexEvidenceError, match="output rate"):
        UsageRates(
            model="fixture-model",
            unit="credits",
            effective_date="2026-08-16",
            source_url="https://learn.chatgpt.com/docs/pricing",
            input_per_million=5.0,
            cached_input_per_million=0.5,
            output_per_million=-1.0,
        )


def run_result(tmp_path: Path, stdout: str) -> CodexRunResult:
    evidence_dir = tmp_path / "evidence" / "cell-1"
    evidence_dir.mkdir(parents=True)
    return CodexRunResult(
        submission=submission(),
        model="fixture-model",
        duration_seconds=1.0,
        stdout=stdout,
        stderr="",
        evidence_dir=evidence_dir,
        evidence_refs=("cell-1/stdout.txt",),
    )


def test_usage_meter_prices_uncached_cached_and_output_tokens(tmp_path: Path) -> None:
    stdout = "\n".join(
        [
            json.dumps({"type": "thread.started", "thread_id": "fixture"}),
            json.dumps(
                {
                    "type": "turn.completed",
                    "usage": {
                        "input_tokens": 1_000_000,
                        "cached_input_tokens": 200_000,
                        "output_tokens": 100_000,
                        "reasoning_output_tokens": 50_000,
                    },
                }
            ),
        ]
    )

    measurement = JsonlUsageCostMeter(rates()).measure(
        run_result(tmp_path, stdout), {}, {}, 0
    )

    assert measurement.cost == 7.1
    assert measurement.evidence_refs == ("cell-1/usage-cost.json",)
    record = json.loads(
        (tmp_path / "evidence" / "cell-1" / "usage-cost.json").read_text("utf-8")
    )
    assert record["usage"]["reasoning_output_tokens"] == 50_000
    assert record["uncached_input_tokens"] == 800_000
    assert record["measured_cost"] == 7.1


def test_usage_parser_sums_multiple_completed_turns() -> None:
    event = {
        "type": "turn.completed",
        "usage": {
            "input_tokens": 10,
            "cached_input_tokens": 2,
            "output_tokens": 3,
            "reasoning_output_tokens": 1,
        },
    }

    usage = parse_jsonl_usage(f"{json.dumps(event)}\n{json.dumps(event)}")

    assert usage == {
        "turn_count": 2,
        "input_tokens": 20,
        "cached_input_tokens": 4,
        "output_tokens": 6,
        "reasoning_output_tokens": 2,
    }


def test_usage_parser_fails_closed_without_completed_usage() -> None:
    with pytest.raises(CodexEvidenceError, match="no completed-turn usage"):
        parse_jsonl_usage(json.dumps({"type": "turn.started"}))


def test_usage_parser_rejects_malformed_jsonl() -> None:
    with pytest.raises(CodexEvidenceError, match="line 1 is not valid JSON"):
        parse_jsonl_usage("not-json")


def test_usage_parser_rejects_completed_turn_without_usage() -> None:
    with pytest.raises(CodexEvidenceError, match="missing usage"):
        parse_jsonl_usage(json.dumps({"type": "turn.completed"}))


def test_usage_parser_rejects_boolean_token_counts() -> None:
    event = {
        "type": "turn.completed",
        "usage": {
            "input_tokens": True,
            "cached_input_tokens": 0,
            "output_tokens": 0,
            "reasoning_output_tokens": 0,
        },
    }

    with pytest.raises(CodexEvidenceError, match="input_tokens"):
        parse_jsonl_usage(json.dumps(event))


def test_usage_parser_rejects_impossible_cached_usage() -> None:
    event = {
        "type": "turn.completed",
        "usage": {
            "input_tokens": 1,
            "cached_input_tokens": 2,
            "output_tokens": 0,
            "reasoning_output_tokens": 0,
        },
    }

    with pytest.raises(CodexEvidenceError, match="cannot exceed"):
        parse_jsonl_usage(json.dumps(event))


def test_usage_meter_rejects_a_rate_card_for_another_model(tmp_path: Path) -> None:
    event = {
        "type": "turn.completed",
        "usage": {
            "input_tokens": 1,
            "cached_input_tokens": 0,
            "output_tokens": 1,
            "reasoning_output_tokens": 0,
        },
    }
    result = run_result(tmp_path, json.dumps(event))
    result = CodexRunResult(
        submission=result.submission,
        model="different-model",
        duration_seconds=result.duration_seconds,
        stdout=result.stdout,
        stderr=result.stderr,
        evidence_dir=result.evidence_dir,
        evidence_refs=result.evidence_refs,
    )

    with pytest.raises(CodexEvidenceError, match="does not match run model"):
        JsonlUsageCostMeter(rates()).measure(result, {}, {}, 0)


def test_usage_meter_requires_an_explicit_run_model(tmp_path: Path) -> None:
    event = {
        "type": "turn.completed",
        "usage": {
            "input_tokens": 1,
            "cached_input_tokens": 0,
            "output_tokens": 1,
            "reasoning_output_tokens": 0,
        },
    }
    result = run_result(tmp_path, json.dumps(event))
    result = CodexRunResult(
        submission=result.submission,
        model=None,
        duration_seconds=result.duration_seconds,
        stdout=result.stdout,
        stderr=result.stderr,
        evidence_dir=result.evidence_dir,
        evidence_refs=result.evidence_refs,
    )

    with pytest.raises(CodexEvidenceError, match="requires an explicit model"):
        JsonlUsageCostMeter(rates()).measure(result, {}, {}, 0)
