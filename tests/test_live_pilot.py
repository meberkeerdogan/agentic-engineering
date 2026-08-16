import json
import shutil
import sys
from datetime import date
from pathlib import Path

import pytest

from agentic_engineering.live_pilot import LivePilotError, run_live_pilot
from agentic_engineering.codex_environment import CodexEnvironmentError

ROOT = Path(__file__).resolve().parents[1]
FAKE_CODEX = ROOT / "tests" / "fixtures" / "fake_live_codex.py"


def project_fixture(tmp_path: Path) -> Path:
    project = tmp_path / "project"
    (project / "examples").mkdir(parents=True)
    shutil.copytree(
        ROOT / "examples" / "live-pilot-template",
        project / "examples" / "live-pilot-template",
    )
    shutil.copy(ROOT / "examples" / "live-pilot.json", project / "examples")
    shutil.copy(ROOT / "examples" / "live-pilot-rates.json", project / "examples")
    shutil.copy(ROOT / "examples" / "codex-environment.json", project / "examples")
    fake_home = project / ".fake-codex-home"
    (fake_home / "tmp").mkdir(parents=True)
    (fake_home / "auth.json").write_text("{}\n", encoding="utf-8")
    return project


def run_offline(project: Path, run_id: str = "offline-001") -> dict:
    return run_live_pilot(
        project,
        project / "examples" / "live-pilot.json",
        run_id,
        command_prefix=(sys.executable, str(FAKE_CODEX)),
        source_codex_home=project / ".fake-codex-home",
        preflight_date=date(2026, 8, 16),
    )


def test_live_pilot_creates_fresh_repo_and_independent_evidence(tmp_path: Path) -> None:
    project = project_fixture(tmp_path)

    summary = run_offline(project)

    run_dir = project / ".agentic-runs" / "offline-001"
    workspace = run_dir / "workspaces" / "median-fix"
    assert summary["claimed_complete"] is True
    assert summary["verified_complete"] is True
    assert summary["regressions"] == 0
    assert summary["measured_cost"] == 0.0071
    assert summary["cost_unit"] == "credits"
    assert (workspace / ".git").is_dir()
    assert "len(ordered) % 2" in (workspace / "calculator.py").read_text("utf-8")
    assert (run_dir / "pilot-summary.json").is_file()
    preflight = json.loads((run_dir / "preflight-report.json").read_text("utf-8"))
    assert preflight["status"] == "passed"
    assert preflight["model_call_performed"] is False
    assert preflight["enabled_plugin_count"] == 0
    assert preflight["enabled_mcp_count"] == 0
    assert preflight["prompt_json_bytes"] < preflight["baseline_prompt_json_bytes"]
    assert summary["preflight_ref"] == "preflight-report.json"
    assert not list((project / ".fake-codex-home" / "tmp").iterdir())
    status = json.loads((run_dir / "pilot-status.json").read_text("utf-8"))
    assert status["status"] == "completed"
    assert any(ref.endswith("evaluation-report.json") for ref in summary["evidence_refs"])
    assert any(ref.endswith("usage-cost.json") for ref in summary["evidence_refs"])


def test_live_pilot_never_overwrites_an_existing_run(tmp_path: Path) -> None:
    project = project_fixture(tmp_path)
    run_offline(project)

    with pytest.raises(LivePilotError, match="will not be overwritten"):
        run_offline(project)


def test_live_pilot_rejects_escaping_template_reference(tmp_path: Path) -> None:
    project = project_fixture(tmp_path)
    config_path = project / "examples" / "live-pilot.json"
    config = json.loads(config_path.read_text("utf-8"))
    config["template_ref"] = "../outside"
    config_path.write_text(json.dumps(config), encoding="utf-8")

    with pytest.raises(LivePilotError, match="escapes the project root"):
        run_offline(project)


def test_live_pilot_requires_path_safe_run_id(tmp_path: Path) -> None:
    project = project_fixture(tmp_path)

    with pytest.raises(LivePilotError, match="path-safe ID"):
        run_offline(project, "../escape")


def test_live_pilot_rejects_missing_spec_before_agent_execution(tmp_path: Path) -> None:
    project = project_fixture(tmp_path)
    (project / "examples" / "live-pilot-template" / "ACTIVE_SPEC.md").unlink()

    with pytest.raises(LivePilotError, match="specification reference does not exist"):
        run_offline(project)


def test_live_pilot_rejects_rate_card_with_undeclared_fields(tmp_path: Path) -> None:
    project = project_fixture(tmp_path)
    rates_path = project / "examples" / "live-pilot-rates.json"
    rates = json.loads(rates_path.read_text("utf-8"))
    rates["surprise"] = 1
    rates_path.write_text(json.dumps(rates), encoding="utf-8")

    with pytest.raises(LivePilotError, match="exactly the version 1 fields"):
        run_offline(project)


def test_live_pilot_blocks_old_codex_before_model_execution(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    project = project_fixture(tmp_path)
    monkeypatch.setenv("FAKE_CODEX_VERSION", "0.146.0")

    with pytest.raises(CodexEnvironmentError, match="older than the policy minimum"):
        run_offline(project)

    run_dir = project / ".agentic-runs" / "offline-001"
    status = json.loads((run_dir / "pilot-status.json").read_text("utf-8"))
    assert status["status"] == "failed"
    assert not (run_dir / "evidence").exists()
    assert not list((project / ".fake-codex-home" / "tmp").iterdir())


def test_live_pilot_blocks_unavailable_model_before_model_execution(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    project = project_fixture(tmp_path)
    monkeypatch.setenv("FAKE_CODEX_MODEL", "different-model")

    with pytest.raises(CodexEnvironmentError, match="absent from the Codex catalog"):
        run_offline(project)

    assert not (project / ".agentic-runs" / "offline-001" / "evidence").exists()


def test_live_pilot_blocks_prompt_over_budget_before_model_execution(tmp_path: Path) -> None:
    project = project_fixture(tmp_path)
    policy_path = project / "examples" / "codex-environment.json"
    policy = json.loads(policy_path.read_text("utf-8"))
    policy["maximum_prompt_json_bytes"] = 10
    policy_path.write_text(json.dumps(policy), encoding="utf-8")

    with pytest.raises(CodexEnvironmentError, match="exceeds the preflight byte budget"):
        run_offline(project)

    assert not (project / ".agentic-runs" / "offline-001" / "evidence").exists()


def test_live_pilot_blocks_stale_rate_card_before_model_execution(tmp_path: Path) -> None:
    project = project_fixture(tmp_path)
    rates_path = project / "examples" / "live-pilot-rates.json"
    rates = json.loads(rates_path.read_text("utf-8"))
    rates["effective_date"] = "2026-01-01"
    rates_path.write_text(json.dumps(rates), encoding="utf-8")

    with pytest.raises(CodexEnvironmentError, match="older than the preflight policy"):
        run_offline(project)

    assert not (project / ".agentic-runs" / "offline-001" / "evidence").exists()
