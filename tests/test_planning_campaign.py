import json
import shutil
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator

from agentic_engineering.planning_campaign import (
    PlanningCampaignError,
    main,
    validate_planning_campaign,
)


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "examples" / "dependency-planning-campaign.json"


def project_fixture(tmp_path: Path) -> Path:
    project = tmp_path / "project"
    examples = project / "examples"
    examples.mkdir(parents=True)
    shutil.copytree(
        ROOT / "examples" / "live-pilot-template",
        examples / "live-pilot-template",
    )
    shutil.copytree(ROOT / "examples" / "task-pack", examples / "task-pack")
    for name in (
        "dependency-planning-campaign.json",
        "dependency-planning-experiment.json",
        "dependency-planning-task-pack.json",
    ):
        shutil.copy(ROOT / "examples" / name, examples)
    return project


def test_campaign_is_ready_without_model_calls() -> None:
    first = validate_planning_campaign(ROOT, MANIFEST)
    second = validate_planning_campaign(ROOT, MANIFEST)
    expected = json.loads(
        (ROOT / "examples" / "expected-planning-campaign-readiness.json").read_text(
            "utf-8"
        )
    )
    manifest_schema = json.loads(
        (ROOT / "schemas" / "planning-campaign.schema.json").read_text("utf-8")
    )
    report_schema = json.loads(
        (ROOT / "schemas" / "planning-campaign-readiness.schema.json").read_text(
            "utf-8"
        )
    )

    assert first == second == expected
    manifest_value = json.loads(MANIFEST.read_text("utf-8"))
    assert not list(Draft202012Validator(manifest_schema).iter_errors(manifest_value))
    assert not list(Draft202012Validator(report_schema).iter_errors(first))
    assert first["status"] == "ready_for_separate_approval"
    assert first["matrix_size"] == 18
    assert first["divergent_plan_count"] == 2
    assert first["negative_control_count"] == 1
    assert first["model_calls_performed"] is False
    assert first["paid_execution_authorized"] is False


def test_cli_writes_readiness_report(tmp_path: Path) -> None:
    output = tmp_path / "readiness.json"

    result = main(
        [
            str(MANIFEST),
            "--project-root",
            str(ROOT),
            "--output",
            str(output),
        ]
    )

    report = json.loads(output.read_text("utf-8"))
    assert result == 0
    assert report["report_id"].startswith("planning-campaign-readiness-")
    assert len(report["fingerprint"]) == 64


def test_shared_execution_core_must_be_identical(tmp_path: Path) -> None:
    project = project_fixture(tmp_path)
    workflow = (
        project
        / "examples"
        / "task-pack"
        / "multi-file-feature"
        / "workflow-adaptive-plan.md"
    )
    workflow.write_text(workflow.read_text("utf-8") + "\nExtra treatment behavior.\n")

    with pytest.raises(PlanningCampaignError, match="differ only in planning policy"):
        validate_planning_campaign(
            project, project / "examples" / "dependency-planning-campaign.json"
        )


def test_changed_plan_expectation_fails_closed(tmp_path: Path) -> None:
    project = project_fixture(tmp_path)
    manifest_path = project / "examples" / "dependency-planning-campaign.json"
    manifest = json.loads(manifest_path.read_text("utf-8"))
    manifest["task_plans"][1]["expected_adaptive_order"] = [
        "inventory",
        "report",
        "tests",
        "audit",
    ]
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")

    with pytest.raises(PlanningCampaignError, match="adaptive order changed"):
        validate_planning_campaign(project, manifest_path)


def test_readiness_cannot_authorize_model_execution(tmp_path: Path) -> None:
    project = project_fixture(tmp_path)
    manifest_path = project / "examples" / "dependency-planning-campaign.json"
    manifest = json.loads(manifest_path.read_text("utf-8"))
    manifest["model_execution_allowed"] = True
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")

    with pytest.raises(PlanningCampaignError, match="prohibit model execution"):
        validate_planning_campaign(project, manifest_path)
