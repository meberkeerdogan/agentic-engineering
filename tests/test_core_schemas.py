import json
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator, FormatChecker


ROOT = Path(__file__).resolve().parents[1]
SCHEMA_EXAMPLE_PAIRS = [
    ("active-spec.schema.json", "active-spec.json"),
    ("evidence-contract.schema.json", "evidence-contract.json"),
    ("verified-state.schema.json", "verified-state.json"),
    ("experiment-record.schema.json", "experiment-record.json"),
    ("project-preferences.schema.json", "project-preferences.json"),
]


def load_json(relative_path: str) -> dict:
    return json.loads((ROOT / relative_path).read_text(encoding="utf-8"))


def assert_unique(records: list[dict], field: str, label: str) -> None:
    values = [record[field] for record in records]
    assert len(values) == len(set(values)), f"duplicate {label}: {values}"


@pytest.mark.parametrize(("schema_name", "example_name"), SCHEMA_EXAMPLE_PAIRS)
def test_schema_and_example_are_valid(schema_name: str, example_name: str) -> None:
    schema = load_json(f"schemas/{schema_name}")
    example = load_json(f"examples/{example_name}")
    Draft202012Validator.check_schema(schema)
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    errors = sorted(validator.iter_errors(example), key=lambda error: list(error.path))
    assert not errors, "\n".join(error.message for error in errors)


def test_active_spec_ids_are_unique() -> None:
    spec = load_json("examples/active-spec.json")
    assert_unique(spec["requirements"], "id", "requirement IDs")
    criteria = [
        criterion
        for requirement in spec["requirements"]
        for criterion in requirement["acceptance_criteria"]
    ]
    assert_unique(criteria, "id", "acceptance criterion IDs")


def test_evidence_contract_references_exist() -> None:
    spec = load_json("examples/active-spec.json")
    contract = load_json("examples/evidence-contract.json")
    criterion_ids = {
        criterion["id"]
        for requirement in spec["requirements"]
        for criterion in requirement["acceptance_criteria"]
    }
    evaluator_ids = {evaluator["id"] for evaluator in contract["evaluators"]}

    assert contract["spec_id"] == spec["id"]
    assert_unique(contract["criteria"], "id", "evidence criterion IDs")
    assert_unique(contract["evaluators"], "id", "evaluator IDs")
    assert all(
        criterion["spec_criterion_id"] in criterion_ids
        for criterion in contract["criteria"]
    )
    assert all(
        evaluator_id in evaluator_ids
        for criterion in contract["criteria"]
        for evaluator_id in criterion["evaluator_ids"]
    )
    assert set(contract["regression_policy"]["protected_evaluator_ids"]) <= evaluator_ids


def test_verified_state_references_exist() -> None:
    state = load_json("examples/verified-state.json")
    work_item_ids = {item["id"] for item in state["work_items"]}
    evidence_ids = {evidence["id"] for evidence in state["evidence"]}

    assert_unique(state["work_items"], "id", "work-item IDs")
    assert_unique(state["decisions"], "id", "decision IDs")
    assert_unique(state["evidence"], "id", "evidence IDs")
    assert all(
        dependency in work_item_ids
        for item in state["work_items"]
        for dependency in item["depends_on"]
    )
    assert all(
        evidence_ref in evidence_ids
        for item in state["work_items"]
        for evidence_ref in item["evidence_refs"]
    )


def test_experiment_ids_are_unique_and_referenced() -> None:
    experiment = load_json("examples/experiment-record.json")
    arms = [experiment["control"], *experiment["treatments"]]
    assert_unique(arms, "id", "experiment arm IDs")
    assert_unique(experiment["tasks"], "id", "experiment task IDs")
    assert_unique(experiment["metrics"], "id", "metric IDs")
    assert_unique(experiment["runs"], "id", "run IDs")

    arm_ids = {arm["id"] for arm in arms}
    task_ids = {task["id"] for task in experiment["tasks"]}
    assert all(run["arm_id"] in arm_ids for run in experiment["runs"])
    assert all(run["task_id"] in task_ids for run in experiment["runs"])
