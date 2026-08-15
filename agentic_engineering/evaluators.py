"""Single-pass, read-only evaluators for reproducible baseline evidence."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any


class EvaluationError(ValueError):
    """Raised when an evidence contract cannot be evaluated safely."""


class ArtifactMissingError(EvaluationError):
    """Raised when a candidate did not produce a declared artifact."""


MISSING = object()
SUPPORTED_TYPES = {"command", "artifact", "rubric", "world_state"}


def _canonical_json(value: Any) -> str:
    return json.dumps(
        value,
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
    )


def _resolve_inside(root: Path, relative_path: str) -> Path:
    root = root.resolve()
    candidate = (root / relative_path).resolve()
    try:
        candidate.relative_to(root)
    except ValueError as error:
        raise EvaluationError(f"artifact path escapes evaluation root: {relative_path}") from error
    return candidate


def _json_pointer(document: Any, pointer: str) -> Any:
    if pointer == "":
        return document
    if not isinstance(pointer, str) or not pointer.startswith("/"):
        raise EvaluationError(f"invalid JSON pointer: {pointer!r}")
    current = document
    for raw_token in pointer[1:].split("/"):
        token = raw_token.replace("~1", "/").replace("~0", "~")
        if isinstance(current, Mapping):
            if token not in current:
                return MISSING
            current = current[token]
        elif isinstance(current, list):
            if not token.isdigit():
                return MISSING
            try:
                current = current[int(token)]
            except IndexError:
                return MISSING
        else:
            return MISSING
    return current


def _assertion_result(document: Any, assertion: Mapping[str, Any]) -> dict[str, Any]:
    pointer = assertion.get("path")
    operator = assertion.get("operator")
    expected = assertion.get("expected")
    actual = _json_pointer(document, pointer)

    try:
        if operator == "exists":
            if not isinstance(expected, bool):
                raise EvaluationError("exists assertions require a boolean expectation")
            passed = (actual is not MISSING) is expected
        elif actual is MISSING:
            passed = False
        elif operator == "equals":
            passed = actual == expected
        elif operator == "not_equals":
            passed = actual != expected
        elif operator == "contains":
            passed = expected in actual
        elif operator == "gte":
            passed = actual >= expected
        elif operator == "lte":
            passed = actual <= expected
        else:
            raise EvaluationError(f"unsupported assertion operator: {operator!r}")
    except TypeError:
        passed = False

    result = {
        "path": pointer,
        "operator": operator,
        "expected": expected,
        "passed": passed,
    }
    if actual is not MISSING:
        result["actual"] = actual
    return result


def _error_result(definition: Mapping[str, Any], message: str) -> dict[str, Any]:
    return {
        "evaluator_id": definition.get("id", "unknown"),
        "type": definition.get("type", "unknown"),
        "outcome": "error",
        "summary": message,
        "artifact_refs": [],
        "details": {},
    }


def _evaluate_command(
    definition: Mapping[str, Any], root: Path
) -> dict[str, Any]:
    command = definition.get("command")
    if not isinstance(command, list) or not command or not all(
        isinstance(part, str) and part for part in command
    ):
        raise EvaluationError("command evaluator requires a non-empty argument array")
    resolved_command = [sys.executable if part == "{python}" else part for part in command]
    timeout = definition.get("timeout_seconds", 60)
    environment = dict(os.environ)
    environment.update({"PYTHONHASHSEED": "0", "TZ": "UTC"})

    try:
        completed = subprocess.run(
            resolved_command,
            cwd=root,
            env=environment,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            shell=False,
            timeout=timeout,
            check=False,
        )
    except subprocess.TimeoutExpired:
        return {
            "evaluator_id": definition["id"],
            "type": "command",
            "outcome": "error",
            "summary": f"command timed out after {timeout} seconds",
            "artifact_refs": [],
            "details": {"command": command, "timeout_seconds": timeout},
        }
    except OSError as error:
        return _error_result(definition, f"command could not start: {error.strerror}")

    expected_exit_code = definition.get("expected_exit_code", 0)
    passed = completed.returncode == expected_exit_code
    return {
        "evaluator_id": definition["id"],
        "type": "command",
        "outcome": "pass" if passed else "fail",
        "summary": (
            f"command exited with expected code {expected_exit_code}"
            if passed
            else f"command exited {completed.returncode}; expected {expected_exit_code}"
        ),
        "artifact_refs": [],
        "details": {
            "command": command,
            "exit_code": completed.returncode,
            "stdout": completed.stdout,
            "stderr": completed.stderr,
        },
    }


def _artifact_details(definition: Mapping[str, Any], root: Path) -> tuple[Path, dict[str, Any]]:
    relative_path = definition.get("artifact")
    if not isinstance(relative_path, str) or not relative_path:
        raise EvaluationError("artifact evaluator requires an artifact path")
    path = _resolve_inside(root, relative_path)
    if not path.is_file():
        raise ArtifactMissingError(f"artifact does not exist: {relative_path}")
    data = path.read_bytes()
    return path, {
        "path": relative_path,
        "bytes": len(data),
        "sha256": hashlib.sha256(data).hexdigest(),
    }


def _evaluate_artifact(
    definition: Mapping[str, Any], root: Path
) -> dict[str, Any]:
    relative_path = definition.get("artifact")
    try:
        _, details = _artifact_details(definition, root)
    except ArtifactMissingError as error:
        return {
            "evaluator_id": definition["id"],
            "type": "artifact",
            "outcome": "fail",
            "summary": str(error),
            "artifact_refs": [relative_path] if isinstance(relative_path, str) else [],
            "details": {},
        }
    except EvaluationError as error:
        return _error_result(definition, str(error))

    failures: list[str] = []
    minimum_bytes = definition.get("min_bytes")
    if minimum_bytes is not None and details["bytes"] < minimum_bytes:
        failures.append(f"artifact has {details['bytes']} bytes; minimum is {minimum_bytes}")
    expected_hash = definition.get("sha256")
    if expected_hash is not None and details["sha256"] != expected_hash:
        failures.append("artifact SHA-256 does not match")

    return {
        "evaluator_id": definition["id"],
        "type": "artifact",
        "outcome": "fail" if failures else "pass",
        "summary": "; ".join(failures) if failures else "artifact checks passed",
        "artifact_refs": [relative_path],
        "details": details,
    }


def _load_json_artifact(
    definition: Mapping[str, Any], root: Path
) -> tuple[str, Any, dict[str, Any]]:
    path, details = _artifact_details(definition, root)
    try:
        document = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        raise EvaluationError(f"artifact is not valid UTF-8 JSON: {details['path']}") from error
    return details["path"], document, details


def _evaluate_world_state(
    definition: Mapping[str, Any], root: Path
) -> dict[str, Any]:
    try:
        relative_path, document, artifact = _load_json_artifact(definition, root)
        assertions = [
            _assertion_result(document, assertion)
            for assertion in definition.get("assertions", [])
        ]
    except EvaluationError as error:
        return _error_result(definition, str(error))
    passed = bool(assertions) and all(item["passed"] for item in assertions)
    return {
        "evaluator_id": definition["id"],
        "type": "world_state",
        "outcome": "pass" if passed else "fail",
        "summary": (
            "all world-state assertions passed"
            if passed
            else "one or more world-state assertions failed"
        ),
        "artifact_refs": [relative_path],
        "details": {"artifact": artifact, "assertions": assertions},
    }


def _evaluate_rubric(
    definition: Mapping[str, Any], root: Path
) -> dict[str, Any]:
    try:
        relative_path, document, artifact = _load_json_artifact(definition, root)
        criteria = []
        earned = 0.0
        total = 0.0
        for criterion in definition.get("rubric", []):
            weight = float(criterion.get("weight", 1.0))
            assertion = _assertion_result(document, criterion)
            item = {
                "id": criterion["id"],
                "description": criterion["description"],
                "weight": weight,
                **assertion,
            }
            criteria.append(item)
            total += weight
            if assertion["passed"]:
                earned += weight
    except (EvaluationError, KeyError, TypeError, ValueError) as error:
        return _error_result(definition, f"invalid rubric evaluation: {error}")

    score = earned / total if total else 0.0
    threshold = float(definition.get("threshold", 1.0))
    passed = bool(criteria) and score >= threshold
    return {
        "evaluator_id": definition["id"],
        "type": "rubric",
        "outcome": "pass" if passed else "fail",
        "summary": f"rubric score {score:.6f}; threshold {threshold:.6f}",
        "artifact_refs": [relative_path],
        "details": {
            "artifact": artifact,
            "score": score,
            "threshold": threshold,
            "criteria": criteria,
        },
    }


def evaluate_definition(
    definition: Mapping[str, Any], root: Path
) -> dict[str, Any]:
    """Evaluate one declared read-only check."""

    evaluator_type = definition.get("type")
    if evaluator_type not in SUPPORTED_TYPES:
        raise EvaluationError(f"unsupported evaluator type: {evaluator_type!r}")
    if definition.get("read_only") is not True:
        return _error_result(definition, "evaluator is not declared read-only")
    if evaluator_type == "command":
        return _evaluate_command(definition, root)
    if evaluator_type == "artifact":
        return _evaluate_artifact(definition, root)
    if evaluator_type == "rubric":
        return _evaluate_rubric(definition, root)
    return _evaluate_world_state(definition, root)


def _validate_contract(contract: Mapping[str, Any], root: Path) -> None:
    for field in ("id", "work_item_id", "spec_id"):
        if not isinstance(contract.get(field), str) or not contract[field]:
            raise EvaluationError(f"contract {field} must be a non-empty string")
    evaluator_definitions = contract.get("evaluators")
    if not isinstance(evaluator_definitions, list) or not evaluator_definitions:
        raise EvaluationError("evidence contract has no evaluators")
    evaluator_ids = []
    for definition in evaluator_definitions:
        if not isinstance(definition, Mapping):
            raise EvaluationError("evaluator definition must be an object")
        evaluator_id = definition.get("id")
        if not isinstance(evaluator_id, str) or not evaluator_id:
            raise EvaluationError("evaluator ID must be a non-empty string")
        if definition.get("type") not in SUPPORTED_TYPES:
            raise EvaluationError(
                f"unsupported evaluator type: {definition.get('type')!r}"
            )
        if definition.get("read_only") is not True:
            raise EvaluationError(f"evaluator {evaluator_id} is not declared read-only")
        evaluator_type = definition["type"]
        if evaluator_type == "command":
            command = definition.get("command")
            if not isinstance(command, list) or not command or not all(
                isinstance(part, str) and part for part in command
            ):
                raise EvaluationError(
                    f"command evaluator {evaluator_id} requires an argument array"
                )
        else:
            artifact = definition.get("artifact")
            if not isinstance(artifact, str) or not artifact:
                raise EvaluationError(
                    f"{evaluator_type} evaluator {evaluator_id} requires an artifact"
                )
            _resolve_inside(root, artifact)
        if evaluator_type == "rubric" and not definition.get("rubric"):
            raise EvaluationError(f"rubric evaluator {evaluator_id} has no criteria")
        if evaluator_type == "world_state" and not definition.get("assertions"):
            raise EvaluationError(
                f"world-state evaluator {evaluator_id} has no assertions"
            )
        evaluator_ids.append(evaluator_id)
    if len(evaluator_ids) != len(set(evaluator_ids)):
        raise EvaluationError("evidence contract contains duplicate evaluator IDs")
    known_evaluators = set(evaluator_ids)

    criteria = contract.get("criteria")
    if not isinstance(criteria, list) or not criteria:
        raise EvaluationError("evidence contract has no criteria")
    criterion_ids = []
    for criterion in criteria:
        if not isinstance(criterion, Mapping):
            raise EvaluationError("criterion must be an object")
        criterion_id = criterion.get("id")
        if not isinstance(criterion_id, str) or not criterion_id:
            raise EvaluationError("criterion ID must be a non-empty string")
        criterion_ids.append(criterion_id)
        evaluator_refs = criterion.get("evaluator_ids")
        if not isinstance(evaluator_refs, list) or not evaluator_refs:
            raise EvaluationError(f"criterion {criterion_id} has no evaluators")
        missing = sorted(set(evaluator_refs) - known_evaluators)
        if missing:
            raise EvaluationError(
                f"criterion {criterion_id} references missing evaluator(s): "
                + ", ".join(missing)
            )
    if len(criterion_ids) != len(set(criterion_ids)):
        raise EvaluationError("evidence contract contains duplicate criterion IDs")

    baselines = contract.get("baselines", [])
    if not isinstance(baselines, list):
        raise EvaluationError("baselines must be an array")
    if not all(isinstance(baseline, Mapping) for baseline in baselines):
        raise EvaluationError("baseline must be an object")
    baseline_ids = [baseline.get("evaluator_id") for baseline in baselines]
    if len(baseline_ids) != len(set(baseline_ids)):
        raise EvaluationError("evidence contract contains duplicate baselines")
    missing_baselines = sorted(set(baseline_ids) - known_evaluators)
    if missing_baselines:
        raise EvaluationError(
            "baselines reference missing evaluator(s): " + ", ".join(missing_baselines)
        )

    protected = set(
        contract.get("regression_policy", {}).get("protected_evaluator_ids", [])
    )
    missing_protected = sorted(protected - known_evaluators)
    if missing_protected:
        raise EvaluationError(
            "regression policy references missing evaluator(s): "
            + ", ".join(missing_protected)
        )


def run_single_pass_baseline(
    contract: Mapping[str, Any], root: Path
) -> dict[str, Any]:
    """Run every evaluator once and derive criterion and regression evidence."""

    if not isinstance(contract, Mapping):
        raise EvaluationError("evidence contract must be an object")
    root = root.resolve()
    if not root.is_dir():
        raise EvaluationError(f"evaluation root does not exist: {root}")
    _validate_contract(contract, root)
    evaluator_definitions = contract.get("evaluators")
    evaluator_results = [
        evaluate_definition(definition, root) for definition in evaluator_definitions
    ]
    evaluator_results.sort(key=lambda item: item["evaluator_id"])
    result_by_id = {item["evaluator_id"]: item for item in evaluator_results}

    criterion_results = []
    for criterion in contract.get("criteria", []):
        evaluator_ids = criterion.get("evaluator_ids", [])
        outcomes = [result_by_id[evaluator_id]["outcome"] for evaluator_id in evaluator_ids]
        outcome = "pass"
        if "error" in outcomes:
            outcome = "error"
        elif "fail" in outcomes or not outcomes:
            outcome = "fail"
        criterion_results.append(
            {
                "criterion_id": criterion["id"],
                "required": criterion["required"],
                "outcome": outcome,
                "evaluator_ids": sorted(evaluator_ids),
            }
        )
    criterion_results.sort(key=lambda item: item["criterion_id"])

    baseline_by_id = {
        baseline["evaluator_id"]: baseline["result"]
        for baseline in contract.get("baselines", [])
    }
    protected = set(
        contract.get("regression_policy", {}).get("protected_evaluator_ids", [])
    )
    regressions = sorted(
        evaluator_id
        for evaluator_id in protected
        if baseline_by_id.get(evaluator_id) == "pass"
        and result_by_id.get(evaluator_id, {}).get("outcome") != "pass"
    )
    required_results = [item for item in criterion_results if item["required"]]
    overall = (
        "pass"
        if required_results
        and all(item["outcome"] == "pass" for item in required_results)
        and not regressions
        else "fail"
    )
    if any(item["outcome"] == "error" for item in required_results):
        overall = "error"

    payload = {
        "version": 1,
        "contract_id": contract["id"],
        "work_item_id": contract["work_item_id"],
        "spec_id": contract["spec_id"],
        "outcome": overall,
        "criterion_results": criterion_results,
        "evaluator_results": evaluator_results,
        "regressions": regressions,
    }
    fingerprint = hashlib.sha256(_canonical_json(payload).encode("utf-8")).hexdigest()
    return {
        **payload,
        "report_id": f"evaluation-{fingerprint[:16]}",
        "fingerprint": fingerprint,
    }


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Run a read-only evidence contract exactly once."
    )
    parser.add_argument("contract", type=Path)
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--output", "-o", type=Path)
    args = parser.parse_args(argv)

    contract = json.loads(args.contract.read_text(encoding="utf-8"))
    report = run_single_pass_baseline(contract, args.root)
    output = json.dumps(report, indent=2, ensure_ascii=False) + "\n"
    if args.output:
        args.output.write_text(output, encoding="utf-8")
    else:
        print(output, end="")
    return 0 if report["outcome"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
