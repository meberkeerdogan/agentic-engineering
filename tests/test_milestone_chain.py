import json
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator

from agentic_engineering.milestone_chain import (
    MilestoneChainError,
    main,
    validate_milestone_chain,
)


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = (
    ROOT
    / "examples"
    / "long-task"
    / "continuous-evolution"
    / "milestone-chain.json"
)


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def test_milestone_chain_validates_isolated_and_continuous_oracles() -> None:
    first = validate_milestone_chain(ROOT, MANIFEST)
    second = validate_milestone_chain(ROOT, MANIFEST)

    assert first == second
    assert first["status"] == "ready"
    assert first["milestone_count"] == 5
    assert first["model_calls_performed"] is False
    assert all(item["initial_target_completion"] == 0.0 for item in first["milestones"])
    assert all(item["isolated_target_completion"] == 1.0 for item in first["milestones"])
    assert all(item["continuous_target_completion"] == 1.0 for item in first["milestones"])
    assert all(item["continuous_isolated_gap"] == 0.0 for item in first["milestones"])
    assert all(item["regressions"] == 0 for item in first["milestones"])
    assert first["omission_probe"]["omitted_milestone_id"] == "m01-ranked-sources"
    assert first["omission_probe"]["final_outcome"] == "fail"
    assert first["omission_probe"]["regressions"] == 1
    assert first["omission_probe"]["strict_target_completion"] == 0.0
    Draft202012Validator(
        load_json(ROOT / "schemas" / "milestone-chain-report.schema.json")
    ).validate(first)


def test_milestone_chain_cli_writes_report(tmp_path: Path) -> None:
    output = tmp_path / "milestone-chain-report.json"

    exit_code = main(
        [
            str(MANIFEST),
            "--project-root",
            str(ROOT),
            "--output",
            str(output),
        ]
    )

    assert exit_code == 0
    assert load_json(output)["status"] == "ready"


def test_future_dependency_is_rejected_before_execution(tmp_path: Path) -> None:
    manifest = load_json(MANIFEST)
    manifest["milestones"][0]["depends_on"] = ["m05-integrated-plan"]
    path = tmp_path / "invalid-chain.json"
    path.write_text(json.dumps(manifest), encoding="utf-8")

    with pytest.raises(MilestoneChainError, match="earlier milestones"):
        validate_milestone_chain(tmp_path, path)


def test_agent_base_excludes_the_combined_future_spec() -> None:
    manifest = load_json(MANIFEST)

    assert set(manifest["base_excluded_paths"]) == {
        "ACTIVE_SPEC.md",
        "workflow-control.md",
    }
    assert all(
        milestone["spec_ref"].startswith(
            "examples/long-task/continuous-evolution/specs/"
        )
        for milestone in manifest["milestones"]
    )
