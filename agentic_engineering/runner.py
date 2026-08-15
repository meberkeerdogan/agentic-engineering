"""Manager-executor-auditor orchestration over the verified state boundary."""

from __future__ import annotations

from collections.abc import Callable, Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Protocol

from .evaluators import run_single_pass_baseline
from .state_store import VerifiedStateStore


class RunnerError(RuntimeError):
    """Raised when an executor or auditor cannot complete its bounded role."""


@dataclass(frozen=True)
class ExecutionRequest:
    run_id: str
    spec_id: str
    work_item_id: str
    attempt: int


@dataclass(frozen=True)
class Submission:
    artifact_refs: tuple[str, ...]
    claim: str
    revision: str


@dataclass(frozen=True)
class AuditRequest:
    run_id: str
    spec_id: str
    work_item_id: str
    artifact_refs: tuple[str, ...]
    revision: str


class Executor(Protocol):
    def execute(self, request: ExecutionRequest) -> Submission: ...


class Auditor(Protocol):
    def audit(self, request: AuditRequest) -> Mapping[str, Any]: ...


class SinglePassAuditor:
    """Read-only M03 auditor backed by one evidence contract and root."""

    def __init__(self, contract: Mapping[str, Any], root: Path):
        self.contract = contract
        self.root = Path(root)

    def audit(self, request: AuditRequest) -> Mapping[str, Any]:
        if self.contract.get("work_item_id") != request.work_item_id:
            raise RunnerError("auditor contract does not match the work item")
        if self.contract.get("spec_id") != request.spec_id:
            raise RunnerError("auditor contract does not match the specification")
        return run_single_pass_baseline(self.contract, self.root)


class VerifiedSingleAgentRunner:
    """Run one ready item through fresh execution and independent audit."""

    def __init__(
        self,
        store: VerifiedStateStore,
        executor_factory: Callable[[], Executor],
        auditor: Auditor,
        timestamp: Callable[[], str],
    ):
        self.store = store
        self.executor_factory = executor_factory
        self.auditor = auditor
        self.timestamp = timestamp
        self._used_executors: list[Executor] = []

    def run(self, work_item_id: str) -> dict[str, Any]:
        state = self.store.state()
        item = next(
            (candidate for candidate in state["work_items"] if candidate["id"] == work_item_id),
            None,
        )
        if item is None:
            raise RunnerError(f"unknown work item: {work_item_id}")
        if item["status"] != "ready":
            raise RunnerError(f"work item {work_item_id} is not ready")

        self.store.start(work_item_id, self.timestamp())
        request = ExecutionRequest(
            run_id=state["run_id"],
            spec_id=state["spec_id"],
            work_item_id=work_item_id,
            attempt=item["attempt_count"] + 1,
        )
        try:
            executor = self.executor_factory()
            if executor is self.auditor or any(
                executor is previous for previous in self._used_executors
            ):
                raise RunnerError("executor factory did not return a fresh executor")
            self._used_executors.append(executor)
            submission = executor.execute(request)
            if not isinstance(submission, Submission):
                raise RunnerError("executor returned an invalid submission")
            self.store.submit(
                work_item_id,
                list(submission.artifact_refs),
                submission.claim,
                self.timestamp(),
            )
        except Exception as error:
            self.store.block(work_item_id, f"executor error: {error}", self.timestamp())
            if isinstance(error, RunnerError):
                raise
            raise RunnerError(f"executor failed: {error}") from error

        audit_request = AuditRequest(
            run_id=state["run_id"],
            spec_id=state["spec_id"],
            work_item_id=work_item_id,
            artifact_refs=submission.artifact_refs,
            revision=submission.revision,
        )
        try:
            report = self.auditor.audit(audit_request)
            return self.store.record_evaluation(
                work_item_id,
                report,
                submission.revision,
                self.timestamp(),
            )
        except Exception as error:
            current = self.store.state()
            current_item = next(
                candidate
                for candidate in current["work_items"]
                if candidate["id"] == work_item_id
            )
            if current_item["status"] == "awaiting_audit":
                self.store.block(
                    work_item_id, f"auditor error: {error}", self.timestamp()
                )
            if isinstance(error, RunnerError):
                raise
            raise RunnerError(f"auditor failed: {error}") from error
