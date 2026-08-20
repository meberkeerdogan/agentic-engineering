import json
import shutil
import sys
from datetime import date
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator, FormatChecker

from agentic_engineering.product import ProductRunError, run_verified_workflow
from test_core_schemas import load_json, schema_registry

ROOT = Path(__file__).resolve().parents[1]
FAKE_CODEX = ROOT / "tests" / "fixtures" / "fake_live_codex.py"
STAMP = "2026-08-21T10:00:00Z"


def product_fixture(tmp_path: Path) -> Path:
    project = tmp_path / "project"
    (project / "examples").mkdir(parents=True)
    shutil.copytree(
        ROOT / "examples" / "live-pilot-template",
        project / "examples" / "live-pilot-template",
    )
    for name in ("product-run.json", "live-pilot-rates.json", "codex-environment.json"):
        shutil.copy(ROOT / "examples" / name, project / "examples")
    fake_home = project / ".fake-codex-home"
    (fake_home / "tmp").mkdir(parents=True)
    (fake_home / "auth.json").write_text("{}\n", encoding="utf-8")
    return project


def run_offline(project: Path, *, confirm: bool = True) -> dict:
    return run_verified_workflow(
        project,
        project / "examples" / "product-run.json",
        "product-001",
        confirm_paid_run=confirm,
        command_prefix=(sys.executable, str(FAKE_CODEX)),
        source_codex_home=project / ".fake-codex-home",
        preflight_date=date(2026, 8, 21),
        timestamp=lambda: STAMP,
    )


def test_product_run_combines_spec_execution_evidence_and_state(tmp_path: Path) -> None:
    project = product_fixture(tmp_path)

    summary = run_offline(project)

    run_dir = project / ".agentic-runs" / "product-001"
    state = json.loads((run_dir / "verified-state.json").read_text(encoding="utf-8"))
    spec = json.loads((run_dir / "active-spec.json").read_text(encoding="utf-8"))
    assert summary["workflow_id"] == "verified-single-agent-v0.1"
    assert summary["status"] == "verified"
    assert summary["verified_complete"] is True
    assert spec["id"] == "median-active-spec"
    assert state["status"] == "verified"
    assert state["best_known_revision"] == summary["workspace_revision"]
    assert (run_dir / "verified-state.jsonl").is_file()
    assert (run_dir / "workspaces" / "median-fix" / ".agentic" / "active-spec.json").is_file()
    validator = Draft202012Validator(
        load_json("schemas/product-summary.schema.json"),
        format_checker=FormatChecker(),
        registry=schema_registry(),
    )
    assert not list(validator.iter_errors(summary))


def test_product_run_requires_explicit_paid_confirmation(tmp_path: Path) -> None:
    project = product_fixture(tmp_path)

    with pytest.raises(ProductRunError, match="confirm-paid-run"):
        run_offline(project, confirm=False)

    assert not (project / ".agentic-runs").exists()


def test_product_run_rejects_nondefault_workflow(tmp_path: Path) -> None:
    project = product_fixture(tmp_path)
    config_path = project / "examples" / "product-run.json"
    config = json.loads(config_path.read_text(encoding="utf-8"))
    config["arm"]["workflow"] = "bounded-phase-memory"
    config_path.write_text(json.dumps(config), encoding="utf-8")

    with pytest.raises(ProductRunError, match="verified-single-agent-v0.1"):
        run_offline(project)

    assert not (project / ".agentic-runs").exists()
