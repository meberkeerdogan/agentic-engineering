import json
from copy import deepcopy
from pathlib import Path

import pytest
from test_core_schemas import load_json

from agentic_engineering.evaluators import (
    EvaluationError,
    evaluate_definition,
    main,
    run_single_pass_baseline,
)

ROOT = Path(__file__).resolve().parents[1]
FIXTURE_ROOT = ROOT / "examples" / "fixture-task"


def fixture_contract() -> dict:
    return load_json("examples/fixture-task/evidence-contract.json")


def evaluator(contract: dict, evaluator_id: str) -> dict:
    return next(item for item in contract["evaluators"] if item["id"] == evaluator_id)


def test_fixture_produces_exact_golden_evidence() -> None:
    report = run_single_pass_baseline(fixture_contract(), FIXTURE_ROOT)

    assert report == load_json("examples/fixture-task/expected-evaluation.json")


def test_repeated_runs_are_byte_stable() -> None:
    first = run_single_pass_baseline(fixture_contract(), FIXTURE_ROOT)
    second = run_single_pass_baseline(fixture_contract(), FIXTURE_ROOT)

    assert json.dumps(first, sort_keys=True) == json.dumps(second, sort_keys=True)


def test_failed_protected_command_is_a_regression() -> None:
    contract = fixture_contract()
    command = evaluator(contract, "fixture-command")
    command["command"] = ["{python}", "-c", "raise SystemExit(2)"]

    report = run_single_pass_baseline(contract, FIXTURE_ROOT)

    assert report["outcome"] == "fail"
    assert report["regressions"] == ["fixture-command"]
    result = next(
        item for item in report["evaluator_results"]
        if item["evaluator_id"] == "fixture-command"
    )
    assert result["outcome"] == "fail"
    assert result["details"]["exit_code"] == 2


def test_artifact_evaluator_rejects_paths_outside_root() -> None:
    definition = deepcopy(evaluator(fixture_contract(), "fixture-artifact"))
    definition["artifact"] = "../outside.json"

    result = evaluate_definition(definition, FIXTURE_ROOT)

    assert result["outcome"] == "error"
    assert "escapes evaluation root" in result["summary"]


def test_rubric_reports_partial_score_as_failure() -> None:
    definition = deepcopy(evaluator(fixture_contract(), "fixture-rubric"))
    definition["rubric"][1]["expected"] = 4

    result = evaluate_definition(definition, FIXTURE_ROOT)

    assert result["outcome"] == "fail"
    assert result["details"]["score"] == pytest.approx(0.4)


def test_world_state_reports_failed_assertion() -> None:
    definition = deepcopy(evaluator(fixture_contract(), "fixture-world-state"))
    definition["assertions"][0]["expected"] = "blocked"

    result = evaluate_definition(definition, FIXTURE_ROOT)

    assert result["outcome"] == "fail"
    assert result["details"]["assertions"][0]["passed"] is False


def test_evaluator_must_be_declared_read_only() -> None:
    definition = deepcopy(evaluator(fixture_contract(), "fixture-artifact"))
    definition["read_only"] = False

    result = evaluate_definition(definition, FIXTURE_ROOT)

    assert result["outcome"] == "error"
    assert result["summary"] == "evaluator is not declared read-only"


def test_missing_evaluator_reference_is_rejected() -> None:
    contract = fixture_contract()
    contract["evaluators"] = [
        item for item in contract["evaluators"] if item["id"] != "fixture-command"
    ]

    with pytest.raises(EvaluationError, match="references missing evaluator"):
        run_single_pass_baseline(contract, FIXTURE_ROOT)


def test_duplicate_evaluator_ids_are_rejected_before_execution(
    tmp_path: Path,
) -> None:
    contract = fixture_contract()
    marker = tmp_path / "must-not-exist.txt"
    command = evaluator(contract, "fixture-command")
    command["command"] = [
        "{python}",
        "-c",
        "from pathlib import Path; Path('must-not-exist.txt').write_text('ran')",
    ]
    contract["evaluators"].append(deepcopy(command))

    with pytest.raises(EvaluationError, match="duplicate evaluator IDs"):
        run_single_pass_baseline(contract, tmp_path)

    assert not marker.exists()


def test_cli_writes_golden_report(tmp_path: Path) -> None:
    output = tmp_path / "evaluation.json"

    exit_code = main(
        [
            str(FIXTURE_ROOT / "evidence-contract.json"),
            "--root",
            str(FIXTURE_ROOT),
            "--output",
            str(output),
        ]
    )

    assert exit_code == 0
    assert json.loads(output.read_text(encoding="utf-8")) == load_json(
        "examples/fixture-task/expected-evaluation.json"
    )
