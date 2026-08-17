import json
import shutil
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator

from agentic_engineering.memory_campaign import (
    MemoryCampaignError,
    main,
    validate_memory_campaign,
)


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "examples" / "phase-memory-campaign.json"


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
        "phase-memory-campaign.json",
        "phase-memory-experiment.json",
        "phase-memory-task-pack.json",
    ):
        shutil.copy(ROOT / "examples" / name, examples)
    return project


def test_campaign_is_ready_without_model_calls() -> None:
    first = validate_memory_campaign(ROOT, MANIFEST)
    second = validate_memory_campaign(ROOT, MANIFEST)
    expected = json.loads(
        (ROOT / "examples" / "expected-phase-memory-campaign-readiness.json").read_text(
            "utf-8"
        )
    )
    manifest_schema = json.loads(
        (ROOT / "schemas" / "memory-campaign.schema.json").read_text("utf-8")
    )
    report_schema = json.loads(
        (ROOT / "schemas" / "memory-campaign-readiness.schema.json").read_text(
            "utf-8"
        )
    )

    assert first == second == expected
    assert not list(
        Draft202012Validator(manifest_schema).iter_errors(
            json.loads(MANIFEST.read_text("utf-8"))
        )
    )
    assert not list(Draft202012Validator(report_schema).iter_errors(first))
    assert first["status"] == "ready_for_separate_approval"
    assert first["matrix_size"] == 18
    assert first["pressure_task_count"] == 2
    assert first["negative_control_count"] == 1
    assert first["model_calls_performed"] is False
    assert first["paid_execution_authorized"] is False


def test_cli_writes_readiness_report(tmp_path: Path) -> None:
    output = tmp_path / "readiness.json"

    result = main(
        [str(MANIFEST), "--project-root", str(ROOT), "--output", str(output)]
    )

    report = json.loads(output.read_text("utf-8"))
    assert result == 0
    assert report["report_id"].startswith("memory-campaign-readiness-")
    assert len(report["fingerprint"]) == 64


def test_shared_execution_core_must_be_identical(tmp_path: Path) -> None:
    project = project_fixture(tmp_path)
    workflow = (
        project
        / "examples"
        / "task-pack"
        / "multi-file-feature"
        / "workflow-phase-memory.md"
    )
    workflow.write_text(workflow.read_text("utf-8") + "\nExtra treatment behavior.\n")

    with pytest.raises(MemoryCampaignError, match="differ only in memory policy"):
        validate_memory_campaign(
            project, project / "examples" / "phase-memory-campaign.json"
        )


def test_changed_retrieval_expectation_fails_closed(tmp_path: Path) -> None:
    project = project_fixture(tmp_path)
    manifest_path = project / "examples" / "phase-memory-campaign.json"
    manifest = json.loads(manifest_path.read_text("utf-8"))
    manifest["task_memories"][1]["expected_retrieved_entry_ids"] = [
        "restock-current"
    ]
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")

    with pytest.raises(MemoryCampaignError, match="retrieved entries changed"):
        validate_memory_campaign(project, manifest_path)


def test_memory_evidence_must_exist(tmp_path: Path) -> None:
    project = project_fixture(tmp_path)
    memory_path = (
        project
        / "examples"
        / "task-pack"
        / "multi-step-evolution"
        / "phase-memory.json"
    )
    memory = json.loads(memory_path.read_text("utf-8"))
    memory["entries"][0]["evidence_refs"] = ["missing-evidence.txt"]
    memory_path.write_text(json.dumps(memory), encoding="utf-8")

    with pytest.raises(MemoryCampaignError, match="evidence reference does not exist"):
        validate_memory_campaign(
            project, project / "examples" / "phase-memory-campaign.json"
        )


def test_readiness_cannot_authorize_model_execution(tmp_path: Path) -> None:
    project = project_fixture(tmp_path)
    manifest_path = project / "examples" / "phase-memory-campaign.json"
    manifest = json.loads(manifest_path.read_text("utf-8"))
    manifest["model_execution_allowed"] = True
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")

    with pytest.raises(MemoryCampaignError, match="prohibit model execution"):
        validate_memory_campaign(project, manifest_path)
