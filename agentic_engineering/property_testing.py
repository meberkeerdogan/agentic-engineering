"""Aggregate independently reviewed complementary property-test evidence."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any


class PropertyTestingError(ValueError):
    """Raised when property proposals, reviews, or results are untrusted."""


ID_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")


def _canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"), sort_keys=True)


def _fingerprint(value: Any) -> str:
    return hashlib.sha256(_canonical_json(value).encode("utf-8")).hexdigest()


def _refs(value: Any) -> bool:
    return isinstance(value, list) and bool(value) and len(value) == len(set(value)) and all(
        isinstance(item, str) and item for item in value
    )


def evaluate_property_evidence(manifest: Mapping[str, Any]) -> dict[str, Any]:
    """Filter proposals through independent review and summarize external results."""

    if manifest.get("version") != 1 or not isinstance(manifest.get("suite_id"), str):
        raise PropertyTestingError("property suite must use version 1 and an ID")
    if not ID_PATTERN.fullmatch(manifest["suite_id"]):
        raise PropertyTestingError("suite ID must be path-safe")
    proposals = manifest.get("proposals")
    reviews = manifest.get("reviews")
    results = manifest.get("results")
    if not all(isinstance(value, list) for value in (proposals, reviews, results)):
        raise PropertyTestingError("proposals, reviews, and results must be arrays")
    proposal_by_id: dict[str, Mapping[str, Any]] = {}
    for proposal in proposals:
        if not isinstance(proposal, Mapping) or not isinstance(proposal.get("id"), str):
            raise PropertyTestingError("property proposals require IDs")
        proposal_id = proposal["id"]
        if proposal_id in proposal_by_id or not ID_PATTERN.fullmatch(proposal_id):
            raise PropertyTestingError("property proposal IDs must be unique and path-safe")
        if proposal.get("proposer_role") != "agent":
            raise PropertyTestingError("property proposals must identify the agent proposer")
        if not all(isinstance(proposal.get(field), str) and proposal[field] for field in ("requirement_id", "statement", "oracle")):
            raise PropertyTestingError("property proposals require requirement, statement, and oracle")
        if not _refs(proposal.get("evidence_refs")):
            raise PropertyTestingError("property proposals require evidence references")
        proposal_by_id[proposal_id] = proposal
    review_by_id: dict[str, Mapping[str, Any]] = {}
    for review in reviews:
        if not isinstance(review, Mapping) or review.get("proposal_id") not in proposal_by_id:
            raise PropertyTestingError("reviews must reference declared proposals")
        proposal_id = review["proposal_id"]
        if proposal_id in review_by_id or review.get("reviewer_role") != "independent_auditor":
            raise PropertyTestingError("every proposal requires one independent review")
        if review.get("verdict") not in {"accepted", "rejected"}:
            raise PropertyTestingError("review verdict must be accepted or rejected")
        if not isinstance(review.get("rationale"), str) or not review["rationale"] or not _refs(review.get("evidence_refs")):
            raise PropertyTestingError("reviews require rationale and evidence")
        review_by_id[proposal_id] = review
    if set(review_by_id) != set(proposal_by_id):
        raise PropertyTestingError("every proposal must receive independent review")
    result_by_id: dict[str, Mapping[str, Any]] = {}
    for result in results:
        if not isinstance(result, Mapping) or result.get("proposal_id") not in proposal_by_id:
            raise PropertyTestingError("results must reference declared proposals")
        proposal_id = result["proposal_id"]
        if proposal_id in result_by_id or review_by_id[proposal_id]["verdict"] != "accepted":
            raise PropertyTestingError("only accepted properties may have one result")
        if result.get("outcome") not in {"pass", "counterexample", "invalid"}:
            raise PropertyTestingError("property result outcome is unsupported")
        if result.get("read_only") is not True or not _refs(result.get("evidence_refs")):
            raise PropertyTestingError("property results must be read-only and evidenced")
        result_by_id[proposal_id] = result
    accepted = sorted(key for key, value in review_by_id.items() if value["verdict"] == "accepted")
    rejected = sorted(set(proposal_by_id) - set(accepted))
    missing = sorted(set(accepted) - set(result_by_id))
    if missing:
        raise PropertyTestingError(f"accepted properties are missing results: {missing}")
    counterexamples = sorted(
        proposal_id for proposal_id, result in result_by_id.items() if result["outcome"] == "counterexample"
    )
    invalid = sorted(
        proposal_id for proposal_id, result in result_by_id.items() if result["outcome"] == "invalid"
    )
    report: dict[str, Any] = {
        "version": 1,
        "suite_id": manifest["suite_id"],
        "source_fingerprint": _fingerprint(manifest),
        "accepted_proposal_ids": accepted,
        "rejected_proposal_ids": rejected,
        "counterexample_proposal_ids": counterexamples,
        "invalid_proposal_ids": invalid,
        "required_follow_up": sorted(set(counterexamples + invalid)),
        "result_count": len(result_by_id),
        "executions": [],
        "state_mutations": [],
    }
    fingerprint = _fingerprint(report)
    report["report_id"] = f"property-evidence-{fingerprint[:16]}"
    report["fingerprint"] = fingerprint
    return report


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    arguments = parser.parse_args(argv)
    report = evaluate_property_evidence(json.loads(arguments.manifest.read_text("utf-8")))
    arguments.output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
