import json
from copy import deepcopy
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator, FormatChecker
from test_core_schemas import load_json, schema_registry

from agentic_engineering.evaluators import run_single_pass_baseline
from agentic_engineering.state_store import StateTransitionError, VerifiedStateStore

ROOT = Path(__file__).resolve().parents[1]
FIXTURE_ROOT = ROOT / "examples" / "fixture-task"
T0 = "2026-08-15T20:00:00Z"
T1 = "2026-08-15T20:01:00Z"
T2 = "2026-08-15T20:02:00Z"
T3 = "2026-08-15T20:03:00Z"
T4 = "2026-08-15T20:04:00Z"


def golden_report() -> dict:
    return load_json("examples/fixture-task/expected-evaluation.json")


def create_store(path: Path, work_items: list[dict] | None = None) -> VerifiedStateStore:
    store = VerifiedStateStore(path)
    store.create(
        "fixture-run",
        "fixture-active-spec",
        work_items or [{"id": "fixture-task", "depends_on": []}],
        T0,
    )
    return store


def test_executor_claim_cannot_verify_work(tmp_path: Path) -> None:
    store = create_store(tmp_path / "state.jsonl")
    store.start("fixture-task", T1)

    state = store.submit(
        "fixture-task", ["solution.json"], "Everything is complete.", T2
    )

    item = state["work_items"][0]
    assert item["status"] == "awaiting_audit"
    assert state["status"] == "running"
    assert item["evidence_refs"] == []


def test_passing_evidence_verifies_and_unlocks_dependencies(tmp_path: Path) -> None:
    store = create_store(
        tmp_path / "state.jsonl",
        [
            {"id": "fixture-task", "depends_on": []},
            {"id": "publish", "depends_on": ["fixture-task"]},
        ],
    )
    store.start("fixture-task", T1)
    store.submit("fixture-task", ["solution.json"], "candidate ready", T2)

    state = store.record_evaluation("fixture-task", golden_report(), "rev-1", T3)

    items = {item["id"]: item for item in state["work_items"]}
    assert items["fixture-task"]["status"] == "verified"
    assert items["publish"]["status"] == "ready"
    assert items["fixture-task"]["evidence_refs"]
    assert state["best_known_revision"] == "rev-1"
    assert state["audit_sequence"] == 1


def test_failed_evidence_rejects_then_allows_retry(tmp_path: Path) -> None:
    contract = load_json("examples/fixture-task/evidence-contract.json")
    command = next(item for item in contract["evaluators"] if item["type"] == "command")
    command["command"] = ["{python}", "-c", "raise SystemExit(2)"]
    failed_report = run_single_pass_baseline(contract, FIXTURE_ROOT)
    store = create_store(tmp_path / "state.jsonl")
    store.start("fixture-task", T1)
    store.submit("fixture-task", ["solution.json"], "candidate ready", T2)

    rejected = store.record_evaluation("fixture-task", failed_report, "rev-bad", T3)
    retried = store.retry("fixture-task", T4)

    assert rejected["work_items"][0]["status"] == "rejected"
    assert rejected["best_known_revision"] is None
    assert retried["work_items"][0]["status"] == "ready"


def test_target_scored_evidence_can_verify_state(tmp_path: Path) -> None:
    contract = load_json(
        "examples/long-task/evaluators/multi-target-upgrade/evidence-contract.json"
    )
    report = run_single_pass_baseline(
        contract, ROOT / "examples" / "long-task" / "multi-target-upgrade"
    )
    store = VerifiedStateStore(tmp_path / "state.jsonl")
    store.create(
        "target-run",
        contract["spec_id"],
        [{"id": contract["work_item_id"], "depends_on": []}],
        T0,
    )
    store.start(contract["work_item_id"], T1)
    store.submit(contract["work_item_id"], ["fulfillment"], "candidate ready", T2)

    state = store.record_evaluation(
        contract["work_item_id"], report, "rev-targets", T3
    )

    assert state["status"] == "rejected"
    assert report["scores"]["target_completion"] == 0.0


def test_target_scores_cannot_contradict_target_evidence(tmp_path: Path) -> None:
    contract = load_json(
        "examples/long-task/evaluators/multi-target-upgrade/evidence-contract.json"
    )
    report = run_single_pass_baseline(
        contract, ROOT / "examples" / "long-task" / "multi-target-upgrade"
    )
    forged = deepcopy(report)
    forged["scores"]["targets_passed"] = 5
    payload = {
        key: forged[key]
        for key in set(forged) - {"report_id", "fingerprint"}
    }
    import hashlib

    canonical = json.dumps(payload, ensure_ascii=False, separators=(",", ":"), sort_keys=True)
    forged["fingerprint"] = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
    forged["report_id"] = f"evaluation-{forged['fingerprint'][:16]}"
    store = VerifiedStateStore(tmp_path / "state.jsonl")
    store.create(
        "target-run",
        contract["spec_id"],
        [{"id": contract["work_item_id"], "depends_on": []}],
        T0,
    )
    store.start(contract["work_item_id"], T1)
    store.submit(contract["work_item_id"], ["fulfillment"], "candidate ready", T2)

    with pytest.raises(StateTransitionError, match="scores contradict"):
        store.record_evaluation(contract["work_item_id"], forged, "rev-targets", T3)


def test_forged_report_is_rejected_without_appending(tmp_path: Path) -> None:
    store = create_store(tmp_path / "state.jsonl")
    store.start("fixture-task", T1)
    store.submit("fixture-task", ["solution.json"], "candidate ready", T2)
    forged = deepcopy(golden_report())
    forged["evaluator_results"][0]["outcome"] = "fail"
    before = len(store.events())

    with pytest.raises(StateTransitionError, match="fingerprint is invalid"):
        store.record_evaluation("fixture-task", forged, "rev-forged", T3)

    assert len(store.events()) == before


def test_invalid_transition_does_not_append(tmp_path: Path) -> None:
    store = create_store(tmp_path / "state.jsonl")
    before = len(store.events())

    with pytest.raises(StateTransitionError, match="cannot submit"):
        store.submit("fixture-task", [], "premature", T1)

    assert len(store.events()) == before


def test_hash_chain_detects_tampering(tmp_path: Path) -> None:
    path = tmp_path / "state.jsonl"
    store = create_store(path)
    event = json.loads(path.read_text(encoding="utf-8"))
    event["payload"]["run_id"] = "tampered"
    path.write_text(json.dumps(event) + "\n", encoding="utf-8")

    with pytest.raises(StateTransitionError, match="event hash is invalid"):
        store.events()


def test_dependency_cycles_are_rejected(tmp_path: Path) -> None:
    store = VerifiedStateStore(tmp_path / "state.jsonl")

    with pytest.raises(StateTransitionError, match="contains a cycle"):
        store.create(
            "run",
            "spec",
            [
                {"id": "A", "depends_on": ["B"]},
                {"id": "B", "depends_on": ["A"]},
            ],
            T0,
        )


def test_timestamps_cannot_move_backwards(tmp_path: Path) -> None:
    store = create_store(tmp_path / "state.jsonl")
    store.start("fixture-task", T2)

    with pytest.raises(StateTransitionError, match="timestamps must be monotonic"):
        store.submit("fixture-task", [], "time travel", T1)


def test_state_and_events_validate_against_schemas(tmp_path: Path) -> None:
    store = create_store(tmp_path / "state.jsonl")
    store.start("fixture-task", T1)
    store.submit("fixture-task", ["solution.json"], "candidate ready", T2)
    state = store.record_evaluation("fixture-task", golden_report(), "rev-1", T3)
    registry = schema_registry()

    state_validator = Draft202012Validator(
        load_json("schemas/verified-state.schema.json"),
        format_checker=FormatChecker(),
        registry=registry,
    )
    event_validator = Draft202012Validator(
        load_json("schemas/state-event.schema.json"),
        format_checker=FormatChecker(),
        registry=registry,
    )

    assert not list(state_validator.iter_errors(state))
    assert all(not list(event_validator.iter_errors(event)) for event in store.events())
