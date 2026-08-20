"""Validate a persistent long-task milestone chain without model execution."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import subprocess
import sys
import tempfile
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

from .evaluators import EvaluationError, run_single_pass_baseline


class MilestoneChainError(ValueError):
    """Raised when a milestone chain is unsafe or internally inconsistent."""


MANIFEST_FIELDS = {
    "version",
    "chain_id",
    "title",
    "base_repository_ref",
    "base_excluded_paths",
    "workflow_ref",
    "evaluator_overlay_ref",
    "milestones",
}
MILESTONE_FIELDS = {
    "id",
    "title",
    "depends_on",
    "spec_ref",
    "oracle_patch_ref",
    "target_id",
    "target_test",
    "protected_tests",
}
ID_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")
TEST_NAME_PATTERN = re.compile(r"^[A-Za-z_][A-Za-z0-9_.]*$")
REQUIRED_PROTECTED_TESTS = {
    "tests.test_existing",
    "evaluator_tests.test_protected",
}


def _canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"), sort_keys=True)


def _fingerprint(value: Any) -> str:
    return hashlib.sha256(_canonical_json(value).encode("utf-8")).hexdigest()


def _load_object(path: Path, label: str) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        raise MilestoneChainError(f"{label} is not valid UTF-8 JSON") from error
    if not isinstance(value, dict):
        raise MilestoneChainError(f"{label} must be a JSON object")
    return value


def _resolve_inside(root: Path, reference: Any, label: str) -> Path:
    if not isinstance(reference, str) or not reference:
        raise MilestoneChainError(f"{label} must be a non-empty relative path")
    relative = Path(reference)
    if relative.is_absolute():
        raise MilestoneChainError(f"{label} must be relative to the project root")
    root = root.resolve()
    candidate = (root / relative).resolve()
    try:
        candidate.relative_to(root)
    except ValueError as error:
        raise MilestoneChainError(f"{label} escapes the project root") from error
    return candidate


def _is_link(path: Path) -> bool:
    is_junction = getattr(path, "is_junction", lambda: False)
    return path.is_symlink() or is_junction()


def _reject_links(root: Path, label: str) -> None:
    if _is_link(root):
        raise MilestoneChainError(f"{label} may not be a filesystem link")
    for path in root.rglob("*"):
        if _is_link(path):
            raise MilestoneChainError(f"{label} may not contain filesystem links")


def _tree_fingerprint(root: Path) -> str:
    entries: list[dict[str, Any]] = []
    for path in sorted(root.rglob("*"), key=lambda item: item.relative_to(root).as_posix()):
        relative = path.relative_to(root).as_posix()
        if relative == ".git" or relative.startswith(".git/"):
            continue
        if "__pycache__" in path.parts:
            continue
        if path.is_file():
            content = path.read_bytes()
            entries.append(
                {
                    "path": relative,
                    "bytes": len(content),
                    "sha256": hashlib.sha256(content).hexdigest(),
                }
            )
    return _fingerprint(entries)


def _run_git(workspace: Path, *arguments: str) -> None:
    completed = subprocess.run(
        ["git", *arguments],
        cwd=workspace,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        shell=False,
        check=False,
    )
    if completed.returncode != 0:
        detail = completed.stderr.strip().splitlines()
        reason = detail[-1] if detail else "unknown Git error"
        raise MilestoneChainError(f"could not prepare oracle state: {reason}")


def _initialize_repository(workspace: Path) -> None:
    _run_git(workspace, "init", "--quiet")
    _run_git(workspace, "add", "--all")
    _run_git(
        workspace,
        "-c",
        "user.name=Milestone Fixture",
        "-c",
        "user.email=fixture@agentic-engineering.invalid",
        "commit",
        "--quiet",
        "-m",
        "Seed milestone fixture",
    )


def _apply_patch(workspace: Path, patch: Path) -> None:
    _run_git(
        workspace,
        "apply",
        "--unidiff-zero",
        "--whitespace=nowarn",
        str(patch),
    )


def _validate_manifest(value: Mapping[str, Any]) -> None:
    if set(value) != MANIFEST_FIELDS or value.get("version") != 1:
        raise MilestoneChainError(
            "milestone chain must contain exactly the version 1 fields"
        )
    for field in (
        "chain_id",
        "title",
        "base_repository_ref",
        "workflow_ref",
        "evaluator_overlay_ref",
    ):
        if not isinstance(value.get(field), str) or not value[field]:
            raise MilestoneChainError(f"{field} must be a non-empty string")
    if not ID_PATTERN.fullmatch(value["chain_id"]):
        raise MilestoneChainError("chain_id must be a path-safe ID")
    excluded = value.get("base_excluded_paths")
    if (
        not isinstance(excluded, list)
        or not excluded
        or any(not isinstance(item, str) or not item for item in excluded)
        or len(excluded) != len(set(excluded))
    ):
        raise MilestoneChainError("base exclusions must be unique relative paths")
    milestones = value.get("milestones")
    if not isinstance(milestones, list) or not 4 <= len(milestones) <= 6:
        raise MilestoneChainError("milestone chains require four to six milestones")

    seen: set[str] = set()
    target_ids: set[str] = set()
    target_tests: list[str] = []
    spec_refs: set[str] = set()
    patch_refs: set[str] = set()
    root_count = 0
    integration_count = 0
    for milestone in milestones:
        if not isinstance(milestone, Mapping) or set(milestone) != MILESTONE_FIELDS:
            raise MilestoneChainError("milestone fields are invalid")
        identifier = milestone.get("id")
        target_id = milestone.get("target_id")
        if not isinstance(identifier, str) or not ID_PATTERN.fullmatch(identifier):
            raise MilestoneChainError("milestone ID must be path-safe")
        if identifier in seen:
            raise MilestoneChainError("milestone IDs must be unique")
        if not isinstance(target_id, str) or not ID_PATTERN.fullmatch(target_id):
            raise MilestoneChainError("target ID must be path-safe")
        if target_id in target_ids:
            raise MilestoneChainError("target IDs must be unique")
        for field in ("title", "spec_ref", "oracle_patch_ref"):
            if not isinstance(milestone.get(field), str) or not milestone[field]:
                raise MilestoneChainError(f"milestone {field} must be non-empty")
        dependencies = milestone.get("depends_on")
        if (
            not isinstance(dependencies, list)
            or any(not isinstance(item, str) for item in dependencies)
            or len(dependencies) != len(set(dependencies))
        ):
            raise MilestoneChainError("milestone dependencies must be unique IDs")
        if not set(dependencies) <= seen:
            raise MilestoneChainError(
                "milestone dependencies must reference earlier milestones"
            )
        if not dependencies:
            root_count += 1
        if len(dependencies) >= 2:
            integration_count += 1
        target_test = milestone.get("target_test")
        protected_tests = milestone.get("protected_tests")
        if not isinstance(target_test, str) or not TEST_NAME_PATTERN.fullmatch(target_test):
            raise MilestoneChainError("target test must be a dotted unittest name")
        if (
            not isinstance(protected_tests, list)
            or any(
                not isinstance(item, str) or not TEST_NAME_PATTERN.fullmatch(item)
                for item in protected_tests
            )
            or len(protected_tests) != len(set(protected_tests))
        ):
            raise MilestoneChainError("protected tests must be unique dotted names")
        if not REQUIRED_PROTECTED_TESTS <= set(protected_tests):
            raise MilestoneChainError("every milestone must protect existing behavior")
        if not set(target_tests) <= set(protected_tests):
            raise MilestoneChainError("every milestone must protect earlier targets")
        if target_test in protected_tests:
            raise MilestoneChainError("a target test cannot also be protected")
        if milestone["spec_ref"] in spec_refs or milestone["oracle_patch_ref"] in patch_refs:
            raise MilestoneChainError("milestone spec and patch references must be unique")
        seen.add(identifier)
        target_ids.add(target_id)
        target_tests.append(target_test)
        spec_refs.add(milestone["spec_ref"])
        patch_refs.add(milestone["oracle_patch_ref"])
    if root_count < 2 or not integration_count:
        raise MilestoneChainError(
            "milestone chains require dependency branches and an integration milestone"
        )


def _build_contract(chain_id: str, milestone: Mapping[str, Any]) -> dict[str, Any]:
    milestone_id = milestone["id"]
    return {
        "version": 1,
        "id": f"{chain_id}-{milestone_id}-evidence",
        "work_item_id": milestone_id,
        "spec_id": f"{chain_id}-{milestone_id}-spec",
        "criteria": [
            {
                "id": f"EC-{milestone_id}-TARGET",
                "spec_criterion_id": f"AC-{milestone_id}-TARGET",
                "description": "The current milestone behavior passes.",
                "target_id": milestone["target_id"],
                "evaluator_ids": ["target-behavior"],
                "required": True,
            },
            {
                "id": f"EC-{milestone_id}-PROTECTED",
                "spec_criterion_id": f"AC-{milestone_id}-PROTECTED",
                "description": "Existing and earlier milestone behavior remains correct.",
                "evaluator_ids": ["protected-behavior"],
                "required": True,
            },
        ],
        "evaluators": [
            {
                "id": "target-behavior",
                "type": "command",
                "command": [
                    "{python}",
                    "-m",
                    "evaluator_tests.run_suite",
                    milestone["target_test"],
                ],
                "expected_exit_code": 0,
                "timeout_seconds": 20,
                "read_only": True,
            },
            {
                "id": "protected-behavior",
                "type": "command",
                "command": [
                    "{python}",
                    "-m",
                    "evaluator_tests.run_suite",
                    *milestone["protected_tests"],
                ],
                "expected_exit_code": 0,
                "timeout_seconds": 20,
                "read_only": True,
            },
        ],
        "baselines": [
            {"evaluator_id": "target-behavior", "result": "fail", "artifact_refs": []},
            {"evaluator_id": "protected-behavior", "result": "pass", "artifact_refs": []},
        ],
        "regression_policy": {
            "protected_evaluator_ids": ["protected-behavior"],
            "exploration_allowed": False,
            "restore_best_known_on_failure": True,
        },
        "evidence_directory": f".agent/evidence/{milestone_id}",
    }


def _evaluate_candidate(
    candidate: Path,
    overlay: Path,
    contract: Mapping[str, Any],
    evaluation_root: Path,
) -> dict[str, Any]:
    if evaluation_root.exists():
        raise MilestoneChainError("evaluation directory already exists")
    shutil.copytree(candidate, evaluation_root, ignore=shutil.ignore_patterns(".git"))
    shutil.copytree(overlay, evaluation_root / "evaluator_tests")
    try:
        return run_single_pass_baseline(contract, evaluation_root)
    except EvaluationError as error:
        raise MilestoneChainError(f"milestone evaluator failed: {error}") from error


def _assert_initial_report(report: Mapping[str, Any], milestone_id: str) -> None:
    protected = next(
        item
        for item in report["evaluator_results"]
        if item["evaluator_id"] == "protected-behavior"
    )
    if (
        report.get("outcome") != "fail"
        or report.get("regressions")
        or report.get("scores", {}).get("targets_passed") != 0
        or protected.get("outcome") != "pass"
    ):
        raise MilestoneChainError(
            f"milestone {milestone_id} does not start with one clean target failure"
        )


def _assert_oracle_report(report: Mapping[str, Any], milestone_id: str) -> None:
    if (
        report.get("outcome") != "pass"
        or report.get("regressions")
        or report.get("scores", {}).get("target_completion") != 1.0
    ):
        raise MilestoneChainError(f"milestone {milestone_id} oracle did not pass")


def validate_milestone_chain(project_root: Path, manifest_path: Path) -> dict[str, Any]:
    """Validate isolated and continuous oracle paths plus one omission probe."""

    project_root = project_root.resolve()
    manifest_path = manifest_path.resolve()
    try:
        manifest_path.relative_to(project_root)
    except ValueError as error:
        raise MilestoneChainError("manifest must be inside the project root") from error
    manifest = _load_object(manifest_path, "milestone-chain manifest")
    _validate_manifest(manifest)

    base = _resolve_inside(project_root, manifest["base_repository_ref"], "base repository")
    overlay = _resolve_inside(project_root, manifest["evaluator_overlay_ref"], "evaluator overlay")
    workflow = _resolve_inside(project_root, manifest["workflow_ref"], "workflow")
    if not base.is_dir() or not overlay.is_dir() or not workflow.is_file():
        raise MilestoneChainError("base repository, evaluator overlay, or workflow is missing")
    _reject_links(base, "base repository")
    _reject_links(overlay, "evaluator overlay")
    excluded_sources = [
        _resolve_inside(base, reference, "base exclusion")
        for reference in manifest["base_excluded_paths"]
    ]
    if any(not path.exists() or path.is_dir() for path in excluded_sources):
        raise MilestoneChainError("base exclusions must name existing files")

    resolved_milestones = []
    for milestone in manifest["milestones"]:
        spec = _resolve_inside(project_root, milestone["spec_ref"], "milestone spec")
        patch = _resolve_inside(project_root, milestone["oracle_patch_ref"], "oracle patch")
        if not spec.is_file() or not patch.is_file():
            raise MilestoneChainError("milestone spec or oracle patch is missing")
        spec_text = spec.read_text(encoding="utf-8")
        if any(token in spec_text for token in ("evaluator_tests", "solution.patch")):
            raise MilestoneChainError("milestone specification leaks evaluator details")
        resolved_milestones.append((milestone, spec, patch))

    with tempfile.TemporaryDirectory(prefix="agentic-engineering-milestones-") as temp:
        temp_root = Path(temp)
        base_candidate = temp_root / "base"
        shutil.copytree(base, base_candidate)
        for source in excluded_sources:
            relative = source.relative_to(base)
            target = (base_candidate / relative).resolve()
            try:
                target.relative_to(base_candidate.resolve())
            except ValueError as error:
                raise MilestoneChainError("base exclusion escapes candidate") from error
            target.unlink()
        shutil.copy2(workflow, base_candidate / "WORKFLOW.md")
        _initialize_repository(base_candidate)
        canonical = base_candidate
        continuous = temp_root / "continuous"
        shutil.copytree(base_candidate, continuous)
        milestone_results = []

        for index, (milestone, spec, patch) in enumerate(resolved_milestones, start=1):
            contract = _build_contract(manifest["chain_id"], milestone)
            pre_report = _evaluate_candidate(
                canonical,
                overlay,
                contract,
                temp_root / f"evaluation-{index}-pre",
            )
            _assert_initial_report(pre_report, milestone["id"])

            isolated = temp_root / f"isolated-{index}"
            shutil.copytree(canonical, isolated)
            shutil.copy2(spec, isolated / "CURRENT_MILESTONE.md")
            _apply_patch(isolated, patch)
            isolated_report = _evaluate_candidate(
                isolated,
                overlay,
                contract,
                temp_root / f"evaluation-{index}-isolated",
            )
            _assert_oracle_report(isolated_report, milestone["id"])

            shutil.copy2(spec, continuous / "CURRENT_MILESTONE.md")
            _apply_patch(continuous, patch)
            continuous_report = _evaluate_candidate(
                continuous,
                overlay,
                contract,
                temp_root / f"evaluation-{index}-continuous",
            )
            _assert_oracle_report(continuous_report, milestone["id"])
            isolated_state = _tree_fingerprint(isolated)
            continuous_state = _tree_fingerprint(continuous)
            if isolated_state != continuous_state or isolated_report != continuous_report:
                raise MilestoneChainError(
                    f"milestone {milestone['id']} oracle paths diverged"
                )
            initial_completion = pre_report["scores"]["target_completion"]
            isolated_completion = isolated_report["scores"]["target_completion"]
            continuous_completion = continuous_report["scores"]["target_completion"]
            milestone_results.append(
                {
                    "id": milestone["id"],
                    "depends_on": milestone["depends_on"],
                    "initial_target_completion": initial_completion,
                    "isolated_target_completion": isolated_completion,
                    "continuous_target_completion": continuous_completion,
                    "continuous_isolated_gap": 0.0,
                    "regressions": len(continuous_report["regressions"]),
                    "state_fingerprint": continuous_state,
                    "evaluation_fingerprint": continuous_report["fingerprint"],
                }
            )
            canonical = isolated

        omission = temp_root / "omission"
        shutil.copytree(base_candidate, omission)
        for milestone, spec, patch in resolved_milestones[1:]:
            shutil.copy2(spec, omission / "CURRENT_MILESTONE.md")
            _apply_patch(omission, patch)
        final_milestone = resolved_milestones[-1][0]
        omission_report = _evaluate_candidate(
            omission,
            overlay,
            _build_contract(manifest["chain_id"], final_milestone),
            temp_root / "evaluation-omission",
        )
        if omission_report["outcome"] == "pass" or not omission_report["regressions"]:
            raise MilestoneChainError("omission probe did not expose accumulated failure")

        payload = {
            "version": 1,
            "chain_id": manifest["chain_id"],
            "status": "ready",
            "manifest_fingerprint": _fingerprint(manifest),
            "base_fingerprint": _tree_fingerprint(base_candidate),
            "milestone_count": len(milestone_results),
            "model_calls_performed": False,
            "milestones": milestone_results,
            "omission_probe": {
                "omitted_milestone_id": resolved_milestones[0][0]["id"],
                "final_outcome": omission_report["outcome"],
                "regressions": len(omission_report["regressions"]),
                "strict_target_completion": omission_report["scores"]["strict_target_completion"],
                "evaluation_fingerprint": omission_report["fingerprint"],
            },
        }
    fingerprint = _fingerprint(payload)
    return {
        **payload,
        "report_id": f"milestone-chain-{fingerprint[:16]}",
        "fingerprint": fingerprint,
    }


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest", type=Path)
    parser.add_argument("--project-root", type=Path, default=Path.cwd())
    parser.add_argument("--output", "-o", type=Path)
    arguments = parser.parse_args(argv)
    report = validate_milestone_chain(arguments.project_root, arguments.manifest)
    output = json.dumps(report, ensure_ascii=False, indent=2) + "\n"
    if arguments.output:
        arguments.output.write_text(output, encoding="utf-8")
    else:
        sys.stdout.write(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
