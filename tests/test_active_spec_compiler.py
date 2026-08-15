import json
from copy import deepcopy
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator, FormatChecker

from agentic_engineering.active_spec import (
    SpecCompileError,
    behavior_fingerprint,
    behavioral_contract,
    compile_history,
    main,
)
from test_core_schemas import load_json, schema_registry


ROOT = Path(__file__).resolve().parents[1]


def direct_history() -> dict:
    return load_json("examples/spec-history-direct.json")


def revised_history() -> dict:
    return load_json("examples/spec-history-revised.json")


def test_contract_equivalent_histories_compile_to_same_active_behavior() -> None:
    direct = compile_history(direct_history())
    revised = compile_history(revised_history())

    assert behavioral_contract(direct) == behavioral_contract(revised)
    assert behavior_fingerprint(direct) == behavior_fingerprint(revised)


def test_compiler_preserves_superseded_requirements_as_lineage() -> None:
    compiled = compile_history(revised_history())
    requirements = {item["id"]: item for item in compiled["requirements"]}

    assert requirements["REQ-LEGACY"]["status"] == "superseded"
    assert requirements["REQ-001"]["supersedes"] == ["REQ-LEGACY"]
    assert "REQ-LEGACY" not in {
        item["id"] for item in behavioral_contract(compiled)["requirements"]
    }


def test_compiled_output_is_canonical_and_schema_valid() -> None:
    history = direct_history()
    history["base_spec"]["sources"].reverse()
    history["base_spec"]["requirements"].reverse()
    compiled = compile_history(history)

    assert compiled == compile_history(direct_history())

    assert compiled["requirements"] == sorted(
        compiled["requirements"], key=lambda item: item["id"]
    )
    schema = load_json("schemas/active-spec.schema.json")
    validator = Draft202012Validator(
        schema,
        format_checker=FormatChecker(),
        registry=schema_registry(),
    )
    assert not list(validator.iter_errors(compiled))


def test_compiler_rejects_out_of_order_revisions() -> None:
    history = revised_history()
    history["revisions"].reverse()

    with pytest.raises(SpecCompileError, match="ordered by recorded_at"):
        compile_history(history)


def test_compiler_rejects_duplicate_revision_ids() -> None:
    history = revised_history()
    duplicate = deepcopy(history["revisions"][0])
    duplicate["recorded_at"] = "2026-08-15T19:30:00Z"
    history["revisions"].append(duplicate)

    with pytest.raises(SpecCompileError, match="duplicate revision id"):
        compile_history(history)


def test_compiler_rejects_missing_supersession_target() -> None:
    history = revised_history()
    history["revisions"][0]["operations"][1]["requirement"]["supersedes"] = [
        "REQ-MISSING"
    ]

    with pytest.raises(SpecCompileError, match="supersedes missing"):
        compile_history(history)


def test_compiler_applies_scope_removals_and_additions() -> None:
    history = direct_history()
    history["revisions"] = [
        {
            "id": "REV-SCOPE",
            "recorded_at": "2026-08-15T20:00:00Z",
            "operations": [
                {"op": "remove_constraint", "value": "Compilation is deterministic."},
                {"op": "add_constraint", "value": "Output is schema-valid."},
                {"op": "remove_out_of_scope", "value": "Executing an agent"},
                {"op": "add_out_of_scope", "value": "Choosing an agent vendor"},
            ],
        }
    ]

    compiled = compile_history(history)

    assert compiled["constraints"] == ["Output is schema-valid."]
    assert compiled["out_of_scope"] == ["Choosing an agent vendor"]


def test_compiler_rejects_history_with_no_active_requirement() -> None:
    history = direct_history()
    history["revisions"] = [
        {
            "id": "REV-REMOVE-ACTIVE",
            "recorded_at": "2026-08-15T20:00:00Z",
            "operations": [
                {"op": "supersede_requirement", "requirement_id": "REQ-001"},
                {"op": "supersede_requirement", "requirement_id": "REQ-002"},
            ],
        }
    ]

    with pytest.raises(SpecCompileError, match="no active requirements"):
        compile_history(history)


def test_compiler_rejects_schema_invalid_base_values() -> None:
    history = direct_history()
    history["base_spec"]["requirements"][0]["priority"] = "urgent"

    with pytest.raises(SpecCompileError, match="invalid priority"):
        compile_history(history)


def test_compiler_rejects_supersession_cycles() -> None:
    history = direct_history()
    first, second = history["base_spec"]["requirements"]
    first["status"] = "superseded"
    first["supersedes"] = [second["id"]]
    second["status"] = "superseded"
    second["supersedes"] = [first["id"]]
    history["base_spec"]["requirements"].append(
        {
            "id": "REQ-ACTIVE",
            "statement": "Keep one requirement active.",
            "priority": "must",
            "status": "active",
            "acceptance_criteria": [
                {"id": "AC-ACTIVE", "statement": "An active requirement exists."}
            ],
            "supersedes": [],
        }
    )

    with pytest.raises(SpecCompileError, match="contains a cycle"):
        compile_history(history)


def test_compiler_rejects_unknown_operations() -> None:
    history = direct_history()
    history["revisions"] = [
        {
            "id": "REV-UNKNOWN",
            "recorded_at": "2026-08-15T20:00:00Z",
            "operations": [{"op": "rewrite_everything"}],
        }
    ]

    with pytest.raises(SpecCompileError, match="unknown revision operation"):
        compile_history(history)


def test_cli_writes_compiled_specification(tmp_path: Path) -> None:
    output = tmp_path / "active-spec.json"

    exit_code = main(
        [
            str(ROOT / "examples" / "spec-history-revised.json"),
            "--output",
            str(output),
        ]
    )

    assert exit_code == 0
    assert json.loads(output.read_text(encoding="utf-8")) == compile_history(
        revised_history()
    )
