from copy import deepcopy
from pathlib import Path

import pytest
from test_core_schemas import load_json

from agentic_engineering.evaluators import run_single_pass_baseline
from agentic_engineering.runner import (
    RunnerError,
    SinglePassAuditor,
    Submission,
    VerifiedSingleAgentRunner,
)
from agentic_engineering.state_store import VerifiedStateStore

ROOT = Path(__file__).resolve().parents[1]
FIXTURE_ROOT = ROOT / "examples" / "fixture-task"


class StaticExecutor:
    def __init__(self, seen: list[object]):
        self.seen = seen

    def execute(self, request):
        self.seen.append(self)
        return Submission(
            artifact_refs=("solution.json",),
            claim="Candidate is ready for independent audit.",
            revision=f"rev-{request.attempt}",
        )


class SequenceAuditor:
    def __init__(self, reports: list[dict]):
        self.reports = iter(reports)

    def audit(self, request):
        return next(self.reports)


def timestamps(count: int = 20):
    values = iter(f"2026-08-15T21:{minute:02d}:00Z" for minute in range(count))
    return lambda: next(values)


def store(path: Path) -> VerifiedStateStore:
    state_store = VerifiedStateStore(path)
    state_store.create(
        "runner-test",
        "fixture-active-spec",
        [{"id": "fixture-task", "depends_on": []}],
        "2026-08-15T20:59:00Z",
    )
    return state_store


def contract() -> dict:
    return load_json("examples/fixture-task/evidence-contract.json")


def test_fresh_executor_and_single_pass_auditor_verify_work(tmp_path: Path) -> None:
    seen: list[object] = []
    runner = VerifiedSingleAgentRunner(
        store(tmp_path / "state.jsonl"),
        lambda: StaticExecutor(seen),
        SinglePassAuditor(contract(), FIXTURE_ROOT),
        timestamps(),
    )

    state = runner.run("fixture-task")

    assert state["status"] == "verified"
    assert state["work_items"][0]["status"] == "verified"
    assert len(seen) == 1
    assert state["evidence"]


def test_each_retry_constructs_a_fresh_executor(tmp_path: Path) -> None:
    failed_contract = contract()
    command = next(
        item for item in failed_contract["evaluators"] if item["type"] == "command"
    )
    command["command"] = ["{python}", "-c", "raise SystemExit(2)"]
    failed = run_single_pass_baseline(failed_contract, FIXTURE_ROOT)
    passed = load_json("examples/fixture-task/expected-evaluation.json")
    state_store = store(tmp_path / "state.jsonl")
    seen: list[object] = []
    clock = timestamps()
    runner = VerifiedSingleAgentRunner(
        state_store,
        lambda: StaticExecutor(seen),
        SequenceAuditor([failed, passed]),
        clock,
    )

    first = runner.run("fixture-task")
    state_store.retry("fixture-task", clock())
    second = runner.run("fixture-task")

    assert first["work_items"][0]["status"] == "rejected"
    assert second["work_items"][0]["status"] == "verified"
    assert second["work_items"][0]["attempt_count"] == 2
    assert len(seen) == 2
    assert seen[0] is not seen[1]


def test_executor_cannot_submit_its_own_evaluation_report(tmp_path: Path) -> None:
    class InvalidExecutor:
        def execute(self, request):
            return {
                "artifact_refs": ["solution.json"],
                "claim": "Trust me",
                "revision": "rev-malicious",
                "report": deepcopy(
                    load_json("examples/fixture-task/expected-evaluation.json")
                ),
            }

    state_store = store(tmp_path / "state.jsonl")
    runner = VerifiedSingleAgentRunner(
        state_store,
        InvalidExecutor,
        SinglePassAuditor(contract(), FIXTURE_ROOT),
        timestamps(),
    )

    with pytest.raises(RunnerError, match="invalid submission"):
        runner.run("fixture-task")

    state = state_store.state()
    assert state["work_items"][0]["status"] == "blocked"
    assert state["evidence"] == []


def test_cached_executor_is_rejected_on_retry(tmp_path: Path) -> None:
    failed_contract = contract()
    command = next(
        item for item in failed_contract["evaluators"] if item["type"] == "command"
    )
    command["command"] = ["{python}", "-c", "raise SystemExit(2)"]
    failed = run_single_pass_baseline(failed_contract, FIXTURE_ROOT)
    cached = StaticExecutor([])
    state_store = store(tmp_path / "state.jsonl")
    clock = timestamps()
    runner = VerifiedSingleAgentRunner(
        state_store,
        lambda: cached,
        SequenceAuditor([failed]),
        clock,
    )
    runner.run("fixture-task")
    state_store.retry("fixture-task", clock())

    with pytest.raises(RunnerError, match="fresh executor"):
        runner.run("fixture-task")

    assert state_store.state()["work_items"][0]["status"] == "blocked"


def test_auditor_contract_mismatch_blocks_without_verification(tmp_path: Path) -> None:
    wrong_contract = contract()
    wrong_contract["spec_id"] = "different-spec"
    state_store = store(tmp_path / "state.jsonl")
    runner = VerifiedSingleAgentRunner(
        state_store,
        lambda: StaticExecutor([]),
        SinglePassAuditor(wrong_contract, FIXTURE_ROOT),
        timestamps(),
    )

    with pytest.raises(RunnerError, match="does not match the specification"):
        runner.run("fixture-task")

    state = state_store.state()
    assert state["work_items"][0]["status"] == "blocked"
    assert state["evidence"] == []
