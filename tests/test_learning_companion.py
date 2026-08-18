import copy
import json
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator

from agentic_engineering.learning_companion import (
    LearningCompanionError,
    LearningCompanionRunner,
    LearningRequest,
    build_learning_report,
    main,
)


ROOT = Path(__file__).resolve().parents[1]


def load(name: str) -> dict:
    return json.loads((ROOT / "examples" / name).read_text("utf-8"))


class ReplayCompanion:
    def __init__(self, submission: dict):
        self.submission = submission
        self.requests: list[LearningRequest] = []

    def teach(self, request: LearningRequest) -> dict:
        self.requests.append(request)
        return copy.deepcopy(self.submission)


def test_fresh_companion_builds_bounded_proposal_only_report() -> None:
    companion = ReplayCompanion(load("learning-companion-submission.json"))
    report = LearningCompanionRunner(lambda: companion).run(
        load("learning-milestone.json")
    )

    expected = load("expected-learning-companion-report.json")
    assert report == expected
    assert report["status"] == "proposed"
    assert report["engineering_state_mutations"] == []
    assert report["verification_claims"] == []
    assert len(companion.requests) == 1
    request = companion.requests[0]
    assert len(request.focus_refs) == 4
    assert "conversation history" not in request.prompt.lower()
    assert "Do not verify engineering work" in request.prompt
    schema = json.loads(
        (ROOT / "schemas/learning-companion-report.schema.json").read_text("utf-8")
    )
    assert not list(Draft202012Validator(schema).iter_errors(report))


def test_disabled_companion_skips_without_creating_agent() -> None:
    milestone = load("learning-milestone.json")
    milestone["companion_policy"]["enabled"] = False

    def forbidden_factory():
        raise AssertionError("disabled companion must not be created")

    report = LearningCompanionRunner(forbidden_factory).run(milestone)
    assert report["status"] == "skipped"
    assert report["agent_invoked"] is False
    assert report["lesson"] is None
    assert report["learning_path_proposal"] is None


def test_runner_rejects_reused_companion_agent() -> None:
    companion = ReplayCompanion(load("learning-companion-submission.json"))
    runner = LearningCompanionRunner(lambda: companion)
    runner.run(load("learning-milestone.json"))

    with pytest.raises(LearningCompanionError, match="fresh agent"):
        runner.run(load("learning-milestone.json"))


def test_proposal_cannot_escape_focus_or_drop_failed_experiments() -> None:
    milestone = load("learning-milestone.json")
    submission = load("learning-companion-submission.json")
    submission["focus_refs"].append("README.md")
    with pytest.raises(LearningCompanionError, match="undeclared focus"):
        build_learning_report(milestone, submission)

    submission = load("learning-companion-submission.json")
    submission["failed_experiment_lessons"].pop()
    with pytest.raises(LearningCompanionError, match="every failed experiment"):
        build_learning_report(milestone, submission)


def test_milestone_rejects_unbound_focus_and_non_proposal_policy() -> None:
    milestone = load("learning-milestone.json")
    milestone["focus_refs"][0] = "README.md"
    with pytest.raises(LearningCompanionError, match="bound to milestone evidence"):
        LearningCompanionRunner(lambda: None).run(milestone)

    milestone = load("learning-milestone.json")
    milestone["companion_policy"]["proposal_only"] = False
    with pytest.raises(LearningCompanionError, match="proposal-only"):
        LearningCompanionRunner(lambda: None).run(milestone)


def test_cli_writes_the_deterministic_report(tmp_path: Path) -> None:
    output = tmp_path / "learning-report.json"
    second_output = tmp_path / "learning-report-second.json"
    arguments = [
        str(ROOT / "examples/learning-milestone.json"),
        str(ROOT / "examples/learning-companion-submission.json"),
    ]
    assert (
        main(
            [
                *arguments,
                "--output",
                str(output),
            ]
        )
        == 0
    )
    assert json.loads(output.read_text("utf-8")) == load(
        "expected-learning-companion-report.json"
    )
    assert main([*arguments, "--output", str(second_output)]) == 0
    assert output.read_bytes() == second_output.read_bytes()
