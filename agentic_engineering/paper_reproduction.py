"""Execute traceable claim-level paper reproductions with explicit deviations."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any


class ReproductionError(ValueError):
    """Raised when reproduction lineage, execution, or rubric evidence is invalid."""


ID_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")


def _canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"), sort_keys=True)


def _fingerprint(value: Any) -> str:
    return hashlib.sha256(_canonical_json(value).encode("utf-8")).hexdigest()


def _hash_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _resolve(root: Path, reference: str) -> Path:
    if not isinstance(reference, str) or not reference:
        raise ReproductionError("artifact references must be non-empty strings")
    candidate = (root / reference).resolve()
    try:
        candidate.relative_to(root)
    except ValueError as error:
        raise ReproductionError(f"reproduction path escapes project root: {reference}") from error
    if candidate.is_symlink() or getattr(candidate, "is_junction", lambda: False)():
        raise ReproductionError("reproduction artifacts may not be links")
    return candidate


def _pointer(value: Any, pointer: str) -> Any:
    if not isinstance(pointer, str) or not pointer.startswith("/"):
        raise ReproductionError("rubric paths must be JSON pointers")
    current = value
    for token in pointer[1:].split("/"):
        token = token.replace("~1", "/").replace("~0", "~")
        if not isinstance(current, Mapping) or token not in current:
            raise ReproductionError(f"rubric path is absent: {pointer}")
        current = current[token]
    return current


def run_reproduction(project_root: Path, manifest: Mapping[str, Any]) -> dict[str, Any]:
    """Verify lineage, execute declared local experiments, and score the rubric."""

    project_root = project_root.resolve()
    if manifest.get("version") != 1 or not isinstance(manifest.get("reproduction_id"), str):
        raise ReproductionError("reproduction must use version 1 and an ID")
    if not ID_PATTERN.fullmatch(manifest["reproduction_id"]):
        raise ReproductionError("reproduction ID must be path-safe")
    paper = manifest.get("paper")
    environment = manifest.get("environment")
    lineage = manifest.get("lineage")
    experiments = manifest.get("experiments")
    rubric = manifest.get("rubric")
    deviations = manifest.get("deviations")
    if not isinstance(paper, Mapping) or not isinstance(environment, Mapping):
        raise ReproductionError("paper and environment are required")
    if not all(isinstance(value, list) for value in (lineage, experiments, rubric, deviations)):
        raise ReproductionError("lineage, experiments, rubric, and deviations must be arrays")
    artifacts = []
    paper_path = _resolve(project_root, paper.get("pdf_ref"))
    if not paper_path.is_file() or _hash_file(paper_path) != paper.get("sha256"):
        raise ReproductionError("paper artifact hash does not match")
    artifacts.append({"ref": paper["pdf_ref"], "sha256": paper["sha256"]})
    for item in lineage:
        if not isinstance(item, Mapping) or item.get("kind") not in {"paper", "reference_code", "derived_fixture", "environment_lock"}:
            raise ReproductionError("lineage entries require supported kinds")
        path = _resolve(project_root, item.get("ref"))
        actual = _hash_file(path) if path.is_file() else None
        if actual is None or actual != item.get("sha256"):
            raise ReproductionError(f"lineage hash does not match: {item.get('ref')}")
        artifacts.append({"ref": item["ref"], "sha256": actual})
    lock_path = _resolve(project_root, environment.get("lock_ref"))
    if not lock_path.is_file() or environment.get("network") != "disabled":
        raise ReproductionError("environment requires a local lock and disabled network")
    experiment_root = _resolve(project_root, manifest.get("experiment_root"))
    if not experiment_root.is_dir():
        raise ReproductionError("experiment root must be a directory")
    results: dict[str, dict[str, Any]] = {}
    for experiment in experiments:
        if not isinstance(experiment, Mapping) or not isinstance(experiment.get("id"), str):
            raise ReproductionError("experiments require IDs")
        experiment_id = experiment["id"]
        if experiment_id in results or not ID_PATTERN.fullmatch(experiment_id):
            raise ReproductionError("experiment IDs must be unique and path-safe")
        command = experiment.get("command")
        timeout = experiment.get("timeout_seconds")
        if not isinstance(command, list) or not command or not all(isinstance(part, str) and part for part in command):
            raise ReproductionError("experiment commands must be argument arrays")
        if isinstance(timeout, bool) or not isinstance(timeout, int) or timeout < 1:
            raise ReproductionError("experiment timeout must be positive")
        resolved_command = [sys.executable if part == "{python}" else part for part in command]
        try:
            completed = subprocess.run(
                resolved_command,
                cwd=experiment_root,
                shell=False,
                capture_output=True,
                text=True,
                encoding="utf-8",
                timeout=timeout,
                check=False,
            )
        except (OSError, subprocess.TimeoutExpired) as error:
            raise ReproductionError(f"experiment failed to execute: {experiment_id}") from error
        if completed.returncode != 0:
            raise ReproductionError(f"experiment exited nonzero: {experiment_id}")
        try:
            observation = json.loads(completed.stdout)
        except json.JSONDecodeError as error:
            raise ReproductionError("experiment stdout must be one JSON value") from error
        if observation != experiment.get("expected_observation"):
            raise ReproductionError(f"experiment observation changed: {experiment_id}")
        results[experiment_id] = {
            "experiment_id": experiment_id,
            "outcome": "matched",
            "observation": observation,
            "stderr_sha256": hashlib.sha256(completed.stderr.encode("utf-8")).hexdigest(),
            "evidence_refs": list(experiment.get("evidence_refs", [])),
        }
    criterion_results = []
    for criterion in rubric:
        if not isinstance(criterion, Mapping) or criterion.get("experiment_id") not in results:
            raise ReproductionError("rubric criteria must reference experiments")
        actual = _pointer(results[criterion["experiment_id"]]["observation"], criterion.get("path"))
        passed = actual == criterion.get("expected")
        criterion_results.append(
            {"id": criterion.get("id"), "passed": passed, "actual": actual, "expected": criterion.get("expected"), "evidence_refs": list(criterion.get("evidence_refs", []))}
        )
    if any(not isinstance(item, Mapping) or not item.get("description") or not item.get("impact") for item in deviations):
        raise ReproductionError("every deviation requires description and impact")
    report: dict[str, Any] = {
        "version": 1,
        "reproduction_id": manifest["reproduction_id"],
        "scope": "claim_level",
        "paper_id": paper.get("id"),
        "claim_id": paper.get("claim_id"),
        "source_fingerprint": _fingerprint(manifest),
        "artifact_hashes": sorted(artifacts, key=lambda item: item["ref"]),
        "environment": dict(environment),
        "experiment_results": [results[key] for key in sorted(results)],
        "criterion_results": criterion_results,
        "outcome": "supported_in_fixture" if criterion_results and all(item["passed"] for item in criterion_results) else "not_supported_in_fixture",
        "deviations": list(deviations),
        "model_calls_performed": False,
    }
    fingerprint = _fingerprint(report)
    report["report_id"] = f"reproduction-{fingerprint[:16]}"
    report["fingerprint"] = fingerprint
    return report


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest", type=Path)
    parser.add_argument("--project-root", type=Path, default=Path.cwd())
    parser.add_argument("--output", type=Path, required=True)
    arguments = parser.parse_args(argv)
    manifest = json.loads(arguments.manifest.read_text("utf-8"))
    report = run_reproduction(arguments.project_root, manifest)
    arguments.output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
