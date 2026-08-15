"""Compile specification revision histories into deterministic active contracts."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from collections.abc import Mapping, Sequence
from copy import deepcopy
from datetime import datetime
from pathlib import Path
from typing import Any


class SpecCompileError(ValueError):
    """Raised when a specification history is inconsistent or incomplete."""


ID_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")
SOURCE_KINDS = {"user", "issue", "file", "paper", "standard", "url"}
SPEC_FIELDS = {
    "version",
    "id",
    "title",
    "objective",
    "status",
    "requirements",
    "constraints",
    "out_of_scope",
    "sources",
    "updated_at",
}
REQUIREMENT_FIELDS = {
    "id",
    "statement",
    "priority",
    "status",
    "acceptance_criteria",
    "supersedes",
}
CRITERION_FIELDS = {"id", "statement"}
SOURCE_FIELDS = {"kind", "reference", "note"}


def _timestamp(value: str, label: str = "revision timestamp") -> datetime:
    try:
        parsed = datetime.fromisoformat(value)
    except (AttributeError, ValueError) as error:
        raise SpecCompileError(f"invalid {label}: {value!r}") from error
    if parsed.tzinfo is None:
        raise SpecCompileError(f"{label} must include a timezone: {value!r}")
    return parsed


def _require_string(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise SpecCompileError(f"{label} must be a non-empty string")
    return value


def _require_id(value: Any, label: str) -> str:
    identifier = _require_string(value, label)
    if not ID_PATTERN.fullmatch(identifier):
        raise SpecCompileError(f"{label} has an invalid format: {identifier!r}")
    return identifier


def _canonical_source(source: Mapping[str, Any]) -> tuple[str, str, str]:
    return (
        str(source.get("kind", "")),
        str(source.get("reference", "")),
        str(source.get("note", "")),
    )


def _validate_spec(spec: Mapping[str, Any]) -> None:
    unexpected_spec_fields = set(spec) - SPEC_FIELDS
    if unexpected_spec_fields:
        raise SpecCompileError(
            "unexpected specification field(s): "
            + ", ".join(sorted(unexpected_spec_fields))
        )
    if spec.get("version") != 1:
        raise SpecCompileError("active specification version must be 1")
    _require_id(spec.get("id"), "specification id")
    _require_string(spec.get("title"), "title")
    _require_string(spec.get("objective"), "objective")
    if spec.get("status") not in {"draft", "active", "superseded", "completed"}:
        raise SpecCompileError(f"invalid specification status: {spec.get('status')!r}")
    _timestamp(spec.get("updated_at"), "updated_at")

    for field in ("constraints", "out_of_scope"):
        values = spec.get(field)
        if not isinstance(values, list):
            raise SpecCompileError(f"{field} must be an array")
        for value in values:
            _require_string(value, f"{field} value")

    sources = spec.get("sources")
    if not isinstance(sources, list) or not sources:
        raise SpecCompileError("compiled specification must contain a source")
    for source in sources:
        if not isinstance(source, Mapping):
            raise SpecCompileError("source must be an object")
        unexpected_source_fields = set(source) - SOURCE_FIELDS
        if unexpected_source_fields:
            raise SpecCompileError(
                "unexpected source field(s): "
                + ", ".join(sorted(unexpected_source_fields))
            )
        if source.get("kind") not in SOURCE_KINDS:
            raise SpecCompileError(f"invalid source kind: {source.get('kind')!r}")
        _require_string(source.get("reference"), "source reference")
        if "note" in source:
            _require_string(source.get("note"), "source note")

    requirements = spec.get("requirements")
    if not isinstance(requirements, list) or not requirements:
        raise SpecCompileError("compiled specification must contain a requirement")

    requirement_ids: set[str] = set()
    criterion_ids: set[str] = set()
    supersession_graph: dict[str, list[str]] = {}
    superseded_targets: set[str] = set()

    for requirement in requirements:
        if not isinstance(requirement, Mapping):
            raise SpecCompileError("requirement must be an object")
        unexpected_requirement_fields = set(requirement) - REQUIREMENT_FIELDS
        if unexpected_requirement_fields:
            raise SpecCompileError(
                "unexpected requirement field(s): "
                + ", ".join(sorted(unexpected_requirement_fields))
            )
        requirement_id = _require_id(requirement.get("id"), "requirement id")
        if requirement_id in requirement_ids:
            raise SpecCompileError(f"duplicate requirement id: {requirement_id}")
        requirement_ids.add(requirement_id)

        _require_string(requirement.get("statement"), f"statement in {requirement_id}")
        if requirement.get("priority") not in {"must", "should", "could"}:
            raise SpecCompileError(
                f"invalid priority in {requirement_id}: {requirement.get('priority')!r}"
            )
        if requirement.get("status") not in {"active", "superseded"}:
            raise SpecCompileError(
                f"invalid requirement status in {requirement_id}: "
                f"{requirement.get('status')!r}"
            )

        criteria = requirement.get("acceptance_criteria")
        if not isinstance(criteria, list) or not criteria:
            raise SpecCompileError(
                f"requirement {requirement_id} must have acceptance criteria"
            )
        for criterion in criteria:
            if not isinstance(criterion, Mapping):
                raise SpecCompileError(
                    f"acceptance criterion in {requirement_id} must be an object"
                )
            unexpected_criterion_fields = set(criterion) - CRITERION_FIELDS
            if unexpected_criterion_fields:
                raise SpecCompileError(
                    "unexpected acceptance criterion field(s): "
                    + ", ".join(sorted(unexpected_criterion_fields))
                )
            criterion_id = _require_id(
                criterion.get("id"), f"criterion id in {requirement_id}"
            )
            if criterion_id in criterion_ids:
                raise SpecCompileError(f"duplicate acceptance criterion id: {criterion_id}")
            criterion_ids.add(criterion_id)
            _require_string(
                criterion.get("statement"), f"criterion statement in {requirement_id}"
            )

        supersedes = requirement.get("supersedes", [])
        if not isinstance(supersedes, list):
            raise SpecCompileError(f"supersedes must be an array in {requirement_id}")
        for target_id in supersedes:
            _require_id(target_id, f"supersession target in {requirement_id}")
        if requirement_id in supersedes:
            raise SpecCompileError(f"requirement {requirement_id} cannot supersede itself")
        supersession_graph[requirement_id] = list(supersedes)
        superseded_targets.update(supersedes)

    missing_targets = superseded_targets - requirement_ids
    if missing_targets:
        raise SpecCompileError(
            "missing superseded requirement(s): " + ", ".join(sorted(missing_targets))
        )

    status_by_id = {item["id"]: item.get("status") for item in requirements}
    incorrectly_active = sorted(
        target for target in superseded_targets if status_by_id[target] != "superseded"
    )
    if incorrectly_active:
        raise SpecCompileError(
            "superseded targets still active: " + ", ".join(incorrectly_active)
        )
    if not any(item.get("status") == "active" for item in requirements):
        raise SpecCompileError("compiled specification has no active requirements")

    visiting: set[str] = set()
    visited: set[str] = set()

    def visit(requirement_id: str) -> None:
        if requirement_id in visiting:
            raise SpecCompileError("supersession graph contains a cycle")
        if requirement_id in visited:
            return
        visiting.add(requirement_id)
        for target in supersession_graph[requirement_id]:
            visit(target)
        visiting.remove(requirement_id)
        visited.add(requirement_id)

    for requirement_id in sorted(requirement_ids):
        visit(requirement_id)


def _canonicalize(spec: dict[str, Any]) -> dict[str, Any]:
    for requirement in spec["requirements"]:
        requirement["acceptance_criteria"] = sorted(
            requirement["acceptance_criteria"], key=lambda item: item["id"]
        )
        requirement["supersedes"] = sorted(set(requirement.get("supersedes", [])))
    spec["requirements"] = sorted(spec["requirements"], key=lambda item: item["id"])
    spec["constraints"] = sorted(set(spec.get("constraints", [])))
    spec["out_of_scope"] = sorted(set(spec.get("out_of_scope", [])))
    sources = {
        _canonical_source(source): source for source in spec.get("sources", [])
    }
    spec["sources"] = [sources[key] for key in sorted(sources)]
    return spec


def compile_history(history: Mapping[str, Any]) -> dict[str, Any]:
    """Apply ordered revisions and return a canonical active specification."""

    if not isinstance(history, Mapping):
        raise SpecCompileError("specification history must be an object")
    if history.get("version") != 1:
        raise SpecCompileError("specification history version must be 1")
    base_spec = history.get("base_spec")
    if not isinstance(base_spec, Mapping):
        raise SpecCompileError("base_spec must be an object")

    spec = deepcopy(dict(base_spec))
    _validate_spec(spec)
    requirements = spec.get("requirements")
    if not isinstance(requirements, list):
        raise SpecCompileError("base_spec requirements must be an array")
    requirement_by_id: dict[str, dict[str, Any]] = {}
    for requirement in requirements:
        requirement_id = _require_id(requirement.get("id"), "requirement id")
        if requirement_id in requirement_by_id:
            raise SpecCompileError(f"duplicate requirement id: {requirement_id}")
        requirement_by_id[requirement_id] = deepcopy(requirement)

    revisions = history.get("revisions")
    if not isinstance(revisions, list):
        raise SpecCompileError("revisions must be an array")

    revision_ids: set[str] = set()
    previous_timestamp: datetime | None = None
    for revision in revisions:
        if not isinstance(revision, Mapping):
            raise SpecCompileError("revision must be an object")
        revision_id = _require_id(revision.get("id"), "revision id")
        if revision_id in revision_ids:
            raise SpecCompileError(f"duplicate revision id: {revision_id}")
        revision_ids.add(revision_id)

        recorded_at = _require_string(revision.get("recorded_at"), "recorded_at")
        current_timestamp = _timestamp(recorded_at)
        if previous_timestamp is not None and current_timestamp < previous_timestamp:
            raise SpecCompileError("revisions must be ordered by recorded_at")
        previous_timestamp = current_timestamp

        operations = revision.get("operations")
        if not isinstance(operations, list) or not operations:
            raise SpecCompileError(f"revision {revision_id} has no operations")

        for operation in operations:
            if not isinstance(operation, Mapping):
                raise SpecCompileError(f"operation in {revision_id} must be an object")
            operation_name = operation.get("op")
            if operation_name == "set_objective":
                spec["objective"] = _require_string(
                    operation.get("value"), "objective"
                )
            elif operation_name == "set_status":
                status = operation.get("value")
                if status not in {"draft", "active", "superseded", "completed"}:
                    raise SpecCompileError(f"invalid specification status: {status!r}")
                spec["status"] = status
            elif operation_name == "upsert_requirement":
                incoming = deepcopy(operation.get("requirement"))
                if not isinstance(incoming, dict):
                    raise SpecCompileError("upsert_requirement requires a requirement")
                requirement_id = _require_id(incoming.get("id"), "requirement id")
                existing = requirement_by_id.get(requirement_id)
                if existing and existing.get("status") == "superseded":
                    raise SpecCompileError(
                        f"cannot reactivate superseded requirement: {requirement_id}"
                    )
                incoming["status"] = "active"
                incoming.setdefault("supersedes", [])
                if not isinstance(incoming["supersedes"], list):
                    raise SpecCompileError(
                        f"supersedes must be an array in {requirement_id}"
                    )
                for target_id in incoming["supersedes"]:
                    _require_id(target_id, f"supersession target in {requirement_id}")
                    if target_id not in requirement_by_id:
                        raise SpecCompileError(
                            f"requirement {requirement_id} supersedes missing {target_id}"
                        )
                    requirement_by_id[target_id]["status"] = "superseded"
                requirement_by_id[requirement_id] = incoming
            elif operation_name == "supersede_requirement":
                requirement_id = _require_id(
                    operation.get("requirement_id"), "requirement_id"
                )
                if requirement_id not in requirement_by_id:
                    raise SpecCompileError(
                        f"cannot supersede missing requirement: {requirement_id}"
                    )
                requirement_by_id[requirement_id]["status"] = "superseded"
            elif operation_name in {
                "add_constraint",
                "remove_constraint",
                "add_out_of_scope",
                "remove_out_of_scope",
            }:
                value = _require_string(operation.get("value"), "operation value")
                field = (
                    "constraints" if "constraint" in operation_name else "out_of_scope"
                )
                values = spec.setdefault(field, [])
                if operation_name.startswith("add_") and value not in values:
                    values.append(value)
                elif operation_name.startswith("remove_"):
                    if value not in values:
                        raise SpecCompileError(
                            f"cannot remove missing {field} value: {value}"
                        )
                    values.remove(value)
            elif operation_name == "add_source":
                source = deepcopy(operation.get("source"))
                if not isinstance(source, dict):
                    raise SpecCompileError("add_source requires a source")
                sources = spec.setdefault("sources", [])
                if _canonical_source(source) not in {
                    _canonical_source(existing_source) for existing_source in sources
                }:
                    sources.append(source)
            else:
                raise SpecCompileError(f"unknown revision operation: {operation_name!r}")

        spec["updated_at"] = recorded_at

    spec["requirements"] = list(requirement_by_id.values())
    _validate_spec(spec)
    return _canonicalize(spec)


def behavioral_contract(spec: Mapping[str, Any]) -> dict[str, Any]:
    """Return only fields that define the specification's current behavior."""

    active_requirements = []
    for requirement in spec.get("requirements", []):
        if requirement.get("status") != "active":
            continue
        active_requirements.append(
            {
                "id": requirement["id"],
                "statement": requirement["statement"],
                "priority": requirement["priority"],
                "acceptance_criteria": sorted(
                    deepcopy(requirement["acceptance_criteria"]),
                    key=lambda item: item["id"],
                ),
            }
        )
    return {
        "title": spec["title"],
        "objective": spec["objective"],
        "status": spec["status"],
        "requirements": sorted(active_requirements, key=lambda item: item["id"]),
        "constraints": sorted(set(spec.get("constraints", []))),
        "out_of_scope": sorted(set(spec.get("out_of_scope", []))),
    }


def behavior_fingerprint(spec: Mapping[str, Any]) -> str:
    """Hash the canonical current behavior, excluding history and provenance."""

    payload = json.dumps(
        behavioral_contract(spec),
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Compile a specification revision history."
    )
    parser.add_argument("history", type=Path)
    parser.add_argument("--output", "-o", type=Path)
    parser.add_argument("--behavior-only", action="store_true")
    parser.add_argument("--fingerprint", action="store_true")
    args = parser.parse_args(argv)

    history = json.loads(args.history.read_text(encoding="utf-8"))
    compiled = compile_history(history)
    if args.fingerprint:
        output = behavior_fingerprint(compiled) + "\n"
    else:
        document = behavioral_contract(compiled) if args.behavior_only else compiled
        output = json.dumps(document, indent=2, ensure_ascii=False) + "\n"

    if args.output:
        args.output.write_text(output, encoding="utf-8")
    else:
        print(output, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
