import json
import shutil
import subprocess
from pathlib import Path

from agentic_engineering.evaluators import run_single_pass_baseline


ROOT = Path(__file__).resolve().parents[1]
LEVEL_ONE = ROOT / "examples" / "long-task" / "multi-target-upgrade"
LEVEL_ONE_EVALUATOR = (
    ROOT / "examples" / "long-task" / "evaluators" / "multi-target-upgrade"
)
LEVEL_ONE_ORACLE = (
    ROOT / "examples" / "long-task" / "oracles" / "multi-target-upgrade" / "solution.patch"
)


def load_contract() -> dict:
    return json.loads(
        (LEVEL_ONE_EVALUATOR / "evidence-contract.json").read_text(encoding="utf-8")
    )


def evaluated_candidate(tmp_path: Path) -> Path:
    candidate = tmp_path / "candidate"
    shutil.copytree(LEVEL_ONE, candidate)
    shutil.copytree(
        LEVEL_ONE_EVALUATOR / "evaluator_tests",
        candidate / "evaluator_tests",
    )
    return candidate


def apply_oracle(candidate: Path) -> None:
    initialized = subprocess.run(
        ["git", "init", "--quiet"],
        cwd=candidate,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        shell=False,
        check=False,
    )
    assert initialized.returncode == 0, initialized.stderr
    completed = subprocess.run(
        [
            "git",
            "apply",
            "--unidiff-zero",
            "--whitespace=nowarn",
            str(LEVEL_ONE_ORACLE),
        ],
        cwd=candidate,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        shell=False,
        check=False,
    )
    assert completed.returncode == 0, completed.stderr


def test_level_one_fixture_has_declared_scale_and_hidden_evaluator() -> None:
    source_files = sorted((LEVEL_ONE / "fulfillment").glob("*.py"))
    source_lines = sum(
        len(path.read_text(encoding="utf-8").splitlines()) for path in source_files
    )

    assert 5 <= len(source_files) <= 20
    assert source_lines >= 500
    assert not (LEVEL_ONE / "evaluator_tests").exists()
    assert not (LEVEL_ONE / "evidence-contract.json").exists()
    assert LEVEL_ONE_ORACLE.is_file()
    assert LEVEL_ONE_ORACLE.read_text(encoding="utf-8").count("diff --git") == 5
    target_ids = {
        item["target_id"]
        for item in load_contract()["criteria"]
        if "target_id" in item
    }
    assert len(target_ids) == 5


def test_level_one_start_fails_targets_without_regressions(tmp_path: Path) -> None:
    candidate = evaluated_candidate(tmp_path)

    report = run_single_pass_baseline(load_contract(), candidate)

    assert report["outcome"] == "fail"
    assert report["regressions"] == []
    assert report["scores"] == {
        "targets_passed": 0,
        "targets_total": 5,
        "target_completion": 0.0,
        "strict_target_completion": 0.0,
    }
    assert all(item["outcome"] == "fail" for item in report["target_results"])
    protected = next(
        item
        for item in report["evaluator_results"]
        if item["evaluator_id"] == "protected-behavior"
    )
    assert protected["outcome"] == "pass"


def test_level_one_oracle_passes_all_hidden_and_protected_checks(
    tmp_path: Path,
) -> None:
    candidate = evaluated_candidate(tmp_path)
    apply_oracle(candidate)

    first = run_single_pass_baseline(load_contract(), candidate)
    second = run_single_pass_baseline(load_contract(), candidate)

    assert first == second
    assert first["outcome"] == "pass"
    assert first["regressions"] == []
    assert first["scores"] == {
        "targets_passed": 5,
        "targets_total": 5,
        "target_completion": 1.0,
        "strict_target_completion": 1.0,
    }
    assert all(item["outcome"] == "pass" for item in first["target_results"])
