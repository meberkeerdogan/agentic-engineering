import json
import os
import shutil
import subprocess
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator

from agentic_engineering.multi_agent import MultiAgentError, run_isolated_tasks


ROOT = Path(__file__).resolve().parents[1]


def git(repo: Path, *args: str, env: dict[str, str] | None = None) -> str:
    result = subprocess.run(
        ["git", *args], cwd=repo, capture_output=True, text=True, check=True, env=env
    )
    return result.stdout.strip()


def repository_fixture(tmp_path: Path) -> Path:
    repo = tmp_path / "repo"
    shutil.copytree(ROOT / "examples/multi-agent-fixture", repo)
    git(repo, "init")
    git(repo, "config", "user.name", "Fixture")
    git(repo, "config", "user.email", "fixture@example.invalid")
    git(repo, "add", ".")
    commit_env = os.environ.copy()
    commit_env["GIT_AUTHOR_DATE"] = "2026-08-15T00:00:00Z"
    commit_env["GIT_COMMITTER_DATE"] = "2026-08-15T00:00:00Z"
    git(repo, "commit", "-m", "fixture", env=commit_env)
    return repo


def manifest() -> dict:
    return json.loads((ROOT / "examples/multi-agent-run.json").read_text("utf-8"))


def test_isolated_dag_integrates_and_validates(tmp_path: Path) -> None:
    repo = repository_fixture(tmp_path)
    run_root = tmp_path / "run"

    report = run_isolated_tasks(repo, manifest(), run_root)

    assert report["parallel_waves"] == [["alpha", "beta"], ["combine"]]
    assert [item["task_id"] for item in report["task_results"]] == [
        "alpha",
        "beta",
        "combine",
    ]
    assert report["validation"]["outcome"] == "pass"
    assert report["conflicts"] == []
    assert report["human_interventions"] == 0
    integration = run_root / report["worktree_refs"]["integration"]
    assert (integration / "combined.txt").read_text("utf-8") == "alpha+beta\n"
    assert git(repo, "status", "--porcelain") == ""
    manifest_schema = json.loads(
        (ROOT / "schemas/multi-agent-run.schema.json").read_text("utf-8")
    )
    report_schema = json.loads(
        (ROOT / "schemas/multi-agent-report.schema.json").read_text("utf-8")
    )
    assert not list(Draft202012Validator(manifest_schema).iter_errors(manifest()))
    assert not list(Draft202012Validator(report_schema).iter_errors(report))


def test_undeclared_change_fails_closed(tmp_path: Path) -> None:
    repo = repository_fixture(tmp_path)
    value = manifest()
    value["tasks"][0]["allowed_paths"] = ["other.txt"]

    with pytest.raises(MultiAgentError, match="undeclared paths"):
        run_isolated_tasks(repo, value, tmp_path / "run")


def test_cycle_fails_before_run_directory_is_created(tmp_path: Path) -> None:
    repo = repository_fixture(tmp_path)
    value = manifest()
    value["tasks"][0]["depends_on"] = ["combine"]
    run_root = tmp_path / "run"

    with pytest.raises(MultiAgentError, match="cycle"):
        run_isolated_tasks(repo, value, run_root)

    assert not run_root.exists()


def test_invalid_validation_fails_before_run_directory_is_created(
    tmp_path: Path,
) -> None:
    repo = repository_fixture(tmp_path)
    value = manifest()
    value["validation"]["timeout_seconds"] = 0
    run_root = tmp_path / "run"

    with pytest.raises(MultiAgentError, match="validation command"):
        run_isolated_tasks(repo, value, run_root)

    assert not run_root.exists()
