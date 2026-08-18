"""Build bounded, proposal-only learning reports from verified milestones."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import Any, Protocol


class LearningCompanionError(ValueError):
    """Raised when milestone evidence or a companion proposal is untrusted."""


ID_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")
MILESTONE_FIELDS = {
    "version",
    "milestone_id",
    "title",
    "outcome",
    "learner",
    "verified_facts",
    "decisions",
    "failed_experiments",
    "focus_refs",
    "learning_path_ref",
    "companion_policy",
}
SUBMISSION_FIELDS = {
    "plain_english_summary",
    "concepts",
    "approach",
    "interpretation",
    "exercise",
    "review_questions",
    "focus_refs",
    "failed_experiment_lessons",
    "learning_path_proposal",
}
POLICY_FIELDS = {
    "enabled",
    "proposal_only",
    "cadence",
    "update_learning_path",
    "include_exercise",
    "include_review_questions",
    "maximum_focus_refs",
}
LEARNING_PATH_FIELDS = {
    "completed_topics",
    "current_topics",
    "exercises",
    "suggested_next_topics",
}


def _canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"), sort_keys=True)


def _fingerprint(value: Any) -> str:
    return hashlib.sha256(_canonical_json(value).encode("utf-8")).hexdigest()


def _text(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise LearningCompanionError(f"{label} must be a non-empty string")
    return value


def _identifier(value: Any, label: str) -> str:
    value = _text(value, label)
    if not ID_PATTERN.fullmatch(value):
        raise LearningCompanionError(f"{label} must be a path-safe ID")
    return value


def _strings(
    value: Any,
    label: str,
    *,
    minimum: int = 0,
    maximum: int | None = None,
) -> list[str]:
    if not isinstance(value, list) or not all(
        isinstance(item, str) and item.strip() for item in value
    ):
        raise LearningCompanionError(f"{label} must be an array of non-empty strings")
    if len(value) < minimum or (maximum is not None and len(value) > maximum):
        raise LearningCompanionError(f"{label} has an invalid number of items")
    if len(value) != len(set(value)):
        raise LearningCompanionError(f"{label} must contain unique items")
    return list(value)


def _safe_ref(value: str) -> bool:
    normalized = value.replace("\\", "/")
    path = PurePosixPath(normalized)
    return (
        not normalized.startswith("/")
        and not re.match(r"^[A-Za-z]:", normalized)
        and ".." not in path.parts
    )


def _refs(
    value: Any,
    label: str,
    *,
    minimum: int = 1,
    maximum: int | None = None,
) -> list[str]:
    refs = _strings(value, label, minimum=minimum, maximum=maximum)
    if any(not _safe_ref(ref) for ref in refs):
        raise LearningCompanionError(f"{label} must contain safe relative references")
    return refs


def _exact_mapping(value: Any, fields: set[str], label: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping) or set(value) != fields:
        raise LearningCompanionError(f"{label} fields do not match the contract")
    return value


def _validate_milestone(milestone: Mapping[str, Any]) -> dict[str, Any]:
    _exact_mapping(milestone, MILESTONE_FIELDS, "milestone")
    if milestone.get("version") != 1:
        raise LearningCompanionError("milestone must use version 1")
    milestone_id = _identifier(milestone.get("milestone_id"), "milestone ID")
    _text(milestone.get("title"), "milestone title")
    if milestone.get("outcome") not in {"verified", "failed", "inconclusive"}:
        raise LearningCompanionError("milestone outcome is unsupported")

    learner = _exact_mapping(
        milestone.get("learner"), {"level", "goals"}, "learner"
    )
    if learner.get("level") not in {"beginner", "intermediate", "advanced"}:
        raise LearningCompanionError("learner level is unsupported")
    _strings(learner.get("goals"), "learner goals", minimum=1, maximum=5)

    evidence_refs: set[str] = set()
    fact_ids: set[str] = set()
    facts = milestone.get("verified_facts")
    if not isinstance(facts, list) or not facts:
        raise LearningCompanionError("milestone requires verified facts")
    for fact in facts:
        fact = _exact_mapping(fact, {"id", "statement", "evidence_refs"}, "fact")
        fact_id = _identifier(fact.get("id"), "fact ID")
        if fact_id in fact_ids:
            raise LearningCompanionError("fact IDs must be unique")
        fact_ids.add(fact_id)
        _text(fact.get("statement"), "fact statement")
        evidence_refs.update(_refs(fact.get("evidence_refs"), "fact evidence"))

    decisions = milestone.get("decisions")
    if not isinstance(decisions, list) or not decisions:
        raise LearningCompanionError("milestone requires at least one design decision")
    decision_ids: set[str] = set()
    selected_approaches: set[str] = set()
    declared_alternatives: set[str] = set()
    for decision in decisions:
        decision = _exact_mapping(
            decision,
            {"id", "selected", "rationale", "alternatives", "evidence_refs"},
            "decision",
        )
        decision_id = _identifier(decision.get("id"), "decision ID")
        if decision_id in decision_ids:
            raise LearningCompanionError("decision IDs must be unique")
        decision_ids.add(decision_id)
        selected_approaches.add(_text(decision.get("selected"), "selected approach"))
        _text(decision.get("rationale"), "decision rationale")
        alternatives = _strings(
            decision.get("alternatives"), "decision alternatives", minimum=1, maximum=4
        )
        if decision["selected"] in alternatives:
            raise LearningCompanionError("selected approach cannot also be an alternative")
        declared_alternatives.update(alternatives)
        evidence_refs.update(
            _refs(decision.get("evidence_refs"), "decision evidence")
        )

    failed_experiments = milestone.get("failed_experiments")
    if not isinstance(failed_experiments, list):
        raise LearningCompanionError("failed experiments must be an array")
    failed_by_id: dict[str, set[str]] = {}
    for experiment in failed_experiments:
        experiment = _exact_mapping(
            experiment,
            {"id", "outcome", "lesson", "evidence_refs"},
            "failed experiment",
        )
        experiment_id = _identifier(experiment.get("id"), "failed experiment ID")
        if experiment_id in failed_by_id:
            raise LearningCompanionError("failed experiment IDs must be unique")
        if experiment.get("outcome") not in {"failed", "inconclusive"}:
            raise LearningCompanionError("failed experiment outcome is unsupported")
        _text(experiment.get("lesson"), "failed experiment lesson")
        experiment_refs = set(
            _refs(experiment.get("evidence_refs"), "failed experiment evidence")
        )
        failed_by_id[experiment_id] = experiment_refs
        evidence_refs.update(experiment_refs)

    policy = _exact_mapping(
        milestone.get("companion_policy"), POLICY_FIELDS, "companion policy"
    )
    if not isinstance(policy.get("enabled"), bool):
        raise LearningCompanionError("companion enabled flag must be boolean")
    if policy.get("proposal_only") is not True:
        raise LearningCompanionError("learning companion must remain proposal-only")
    if policy.get("cadence") != "meaningful_milestones":
        raise LearningCompanionError("learning companion cadence must be milestone-bound")
    for field in (
        "update_learning_path",
        "include_exercise",
        "include_review_questions",
    ):
        if not isinstance(policy.get(field), bool):
            raise LearningCompanionError(f"companion policy {field} must be boolean")
    maximum_focus_refs = policy.get("maximum_focus_refs")
    if (
        isinstance(maximum_focus_refs, bool)
        or not isinstance(maximum_focus_refs, int)
        or not 1 <= maximum_focus_refs <= 4
    ):
        raise LearningCompanionError("maximum focus references must be between 1 and 4")

    focus_refs = _refs(
        milestone.get("focus_refs"),
        "focus references",
        maximum=maximum_focus_refs,
    )
    if not set(focus_refs) <= evidence_refs:
        raise LearningCompanionError("focus references must be bound to milestone evidence")
    learning_path_ref = _text(
        milestone.get("learning_path_ref"), "learning path reference"
    )
    if not _safe_ref(learning_path_ref):
        raise LearningCompanionError("learning path reference must be safe and relative")
    return {
        "milestone_id": milestone_id,
        "evidence_refs": evidence_refs,
        "selected_approaches": selected_approaches,
        "declared_alternatives": declared_alternatives,
        "failed_by_id": failed_by_id,
        "focus_refs": set(focus_refs),
        "policy": policy,
    }


def render_learning_prompt(milestone: Mapping[str, Any]) -> str:
    """Render a bounded teaching prompt without conversation history."""

    _validate_milestone(milestone)
    packet = {
        key: milestone[key]
        for key in (
            "milestone_id",
            "title",
            "outcome",
            "learner",
            "verified_facts",
            "decisions",
            "failed_experiments",
            "focus_refs",
            "learning_path_ref",
            "companion_policy",
        )
    }
    return (
        "You are an optional Learning Companion, separate from the engineering agent.\n"
        "Use only the bounded milestone packet and its declared focus references. "
        "Explain unfamiliar ideas in plain English before technical terminology. "
        "Preserve failed and inconclusive experiments. Do not verify engineering work, "
        "modify files, or claim that unsupported conclusions are proven. Return the "
        "structured lesson proposal required by the learning-companion contract.\n\n"
        f"Milestone packet:\n{json.dumps(packet, ensure_ascii=False, indent=2)}"
    )


@dataclass(frozen=True)
class LearningRequest:
    milestone_id: str
    learner_level: str
    goals: tuple[str, ...]
    prompt: str
    focus_refs: tuple[str, ...]
    allowed_evidence_refs: tuple[str, ...]


class LearningCompanion(Protocol):
    def teach(self, request: LearningRequest) -> Mapping[str, Any]: ...


def _lesson_submission(
    milestone: Mapping[str, Any], submission: Mapping[str, Any]
) -> dict[str, Any]:
    validated = _validate_milestone(milestone)
    _exact_mapping(submission, SUBMISSION_FIELDS, "learning companion submission")
    policy = validated["policy"]

    summary = _text(submission.get("plain_english_summary"), "plain-English summary")
    concepts = submission.get("concepts")
    if not isinstance(concepts, list) or not 1 <= len(concepts) <= 5:
        raise LearningCompanionError("lesson requires one to five concepts")
    normalized_concepts = []
    technical_terms: set[str] = set()
    for concept in concepts:
        concept = _exact_mapping(
            concept, {"plain_english", "technical_term"}, "learning concept"
        )
        plain = _text(concept.get("plain_english"), "plain-English concept")
        term = _text(concept.get("technical_term"), "technical term")
        if term in technical_terms:
            raise LearningCompanionError("technical terms must be unique")
        technical_terms.add(term)
        normalized_concepts.append({"plain_english": plain, "technical_term": term})

    approach = _exact_mapping(
        submission.get("approach"),
        {"selected", "rationale", "alternatives"},
        "lesson approach",
    )
    selected = _text(approach.get("selected"), "lesson selected approach")
    if selected not in validated["selected_approaches"]:
        raise LearningCompanionError("lesson selected approach is not declared")
    rationale = _text(approach.get("rationale"), "lesson approach rationale")
    alternatives = _strings(
        approach.get("alternatives"), "lesson alternatives", minimum=1, maximum=4
    )
    if not set(alternatives) <= validated["declared_alternatives"]:
        raise LearningCompanionError("lesson alternatives are not declared")

    interpretation = _exact_mapping(
        submission.get("interpretation"),
        {"supported", "not_supported"},
        "lesson interpretation",
    )
    supported = _strings(
        interpretation.get("supported"), "supported interpretations", minimum=1, maximum=4
    )
    not_supported = _strings(
        interpretation.get("not_supported"),
        "unsupported interpretations",
        minimum=1,
        maximum=4,
    )

    exercise = submission.get("exercise")
    if policy["include_exercise"]:
        exercise = _text(exercise, "learning exercise")
    elif exercise is not None:
        raise LearningCompanionError("exercise must be null when disabled")
    questions = _strings(
        submission.get("review_questions"),
        "review questions",
        minimum=2 if policy["include_review_questions"] else 0,
        maximum=5,
    )
    if not policy["include_review_questions"] and questions:
        raise LearningCompanionError("review questions must be empty when disabled")

    focus_refs = _refs(
        submission.get("focus_refs"),
        "lesson focus references",
        maximum=policy["maximum_focus_refs"],
    )
    if not set(focus_refs) <= validated["focus_refs"]:
        raise LearningCompanionError("lesson references undeclared focus material")

    failed_lessons = submission.get("failed_experiment_lessons")
    if not isinstance(failed_lessons, list):
        raise LearningCompanionError("failed experiment lessons must be an array")
    normalized_failed = []
    seen_failed: set[str] = set()
    for lesson in failed_lessons:
        lesson = _exact_mapping(
            lesson,
            {"experiment_id", "lesson", "evidence_refs"},
            "failed experiment lesson",
        )
        experiment_id = _identifier(
            lesson.get("experiment_id"), "failed experiment lesson ID"
        )
        if experiment_id in seen_failed or experiment_id not in validated["failed_by_id"]:
            raise LearningCompanionError("failed experiment lesson is duplicate or undeclared")
        seen_failed.add(experiment_id)
        refs = _refs(lesson.get("evidence_refs"), "failed experiment lesson evidence")
        if not set(refs) <= validated["failed_by_id"][experiment_id]:
            raise LearningCompanionError("failed experiment lesson evidence is unbound")
        normalized_failed.append(
            {
                "experiment_id": experiment_id,
                "lesson": _text(lesson.get("lesson"), "failed experiment lesson"),
                "evidence_refs": refs,
            }
        )
    if seen_failed != set(validated["failed_by_id"]):
        raise LearningCompanionError("every failed experiment must remain in the lesson")

    proposal = submission.get("learning_path_proposal")
    normalized_proposal = None
    if policy["update_learning_path"]:
        proposal = _exact_mapping(proposal, LEARNING_PATH_FIELDS, "learning path proposal")
        normalized_proposal = {
            field: _strings(proposal.get(field), f"learning path {field}", maximum=5)
            for field in sorted(LEARNING_PATH_FIELDS)
        }
        if not any(normalized_proposal.values()):
            raise LearningCompanionError("learning path proposal cannot be empty")
    elif proposal is not None:
        raise LearningCompanionError("learning path proposal must be null when disabled")

    return {
        "plain_english_summary": summary,
        "concepts": normalized_concepts,
        "approach": {
            "selected": selected,
            "rationale": rationale,
            "alternatives": alternatives,
        },
        "interpretation": {
            "supported": supported,
            "not_supported": not_supported,
        },
        "exercise": exercise,
        "review_questions": questions,
        "focus_refs": focus_refs,
        "failed_experiment_lessons": normalized_failed,
        "learning_path_proposal": normalized_proposal,
    }


def _finalize(report: dict[str, Any]) -> dict[str, Any]:
    fingerprint = _fingerprint(report)
    report["report_id"] = f"learning-companion-{fingerprint[:16]}"
    report["fingerprint"] = fingerprint
    return report


def build_learning_report(
    milestone: Mapping[str, Any], submission: Mapping[str, Any]
) -> dict[str, Any]:
    """Validate one companion proposal and bind it to milestone evidence."""

    validated = _validate_milestone(milestone)
    if not validated["policy"]["enabled"]:
        raise LearningCompanionError("disabled companion cannot accept a submission")
    lesson = _lesson_submission(milestone, submission)
    return _finalize(
        {
            "version": 1,
            "milestone_id": validated["milestone_id"],
            "source_fingerprint": _fingerprint(milestone),
            "status": "proposed",
            "learner_level": milestone["learner"]["level"],
            "agent_invoked": True,
            "lesson": {
                "plain_english_summary": lesson["plain_english_summary"],
                "concepts": lesson["concepts"],
                "approach": lesson["approach"],
                "interpretation": lesson["interpretation"],
                "exercise": lesson["exercise"],
                "review_questions": lesson["review_questions"],
                "focus_refs": lesson["focus_refs"],
                "failed_experiment_lessons": lesson[
                    "failed_experiment_lessons"
                ],
            },
            "learning_path_proposal": lesson["learning_path_proposal"],
            "engineering_state_mutations": [],
            "verification_claims": [],
        }
    )


def _skipped_report(milestone: Mapping[str, Any]) -> dict[str, Any]:
    validated = _validate_milestone(milestone)
    return _finalize(
        {
            "version": 1,
            "milestone_id": validated["milestone_id"],
            "source_fingerprint": _fingerprint(milestone),
            "status": "skipped",
            "learner_level": milestone["learner"]["level"],
            "agent_invoked": False,
            "lesson": None,
            "learning_path_proposal": None,
            "engineering_state_mutations": [],
            "verification_claims": [],
        }
    )


class LearningCompanionRunner:
    """Invoke a fresh companion only for enabled, bounded milestones."""

    def __init__(self, companion_factory: Callable[[], LearningCompanion]):
        self.companion_factory = companion_factory
        self._used_companions: list[LearningCompanion] = []

    def run(self, milestone: Mapping[str, Any]) -> dict[str, Any]:
        validated = _validate_milestone(milestone)
        if not validated["policy"]["enabled"]:
            return _skipped_report(milestone)
        companion = self.companion_factory()
        if any(companion is used for used in self._used_companions):
            raise LearningCompanionError("companion factory did not return a fresh agent")
        self._used_companions.append(companion)
        request = LearningRequest(
            milestone_id=validated["milestone_id"],
            learner_level=milestone["learner"]["level"],
            goals=tuple(milestone["learner"]["goals"]),
            prompt=render_learning_prompt(milestone),
            focus_refs=tuple(milestone["focus_refs"]),
            allowed_evidence_refs=tuple(sorted(validated["evidence_refs"])),
        )
        proposal = companion.teach(request)
        return build_learning_report(milestone, proposal)


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("milestone", type=Path)
    parser.add_argument("submission", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    arguments = parser.parse_args(argv)
    milestone = json.loads(arguments.milestone.read_text(encoding="utf-8"))
    submission = json.loads(arguments.submission.read_text(encoding="utf-8"))
    report = build_learning_report(milestone, submission)
    arguments.output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
