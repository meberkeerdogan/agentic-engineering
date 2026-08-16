# M04: Verified State Store

**Status:** Implemented

## Why This Module Exists

An agent saying “done” is a claim, not proof. This module stores run progress as an append-only event log and derives current state by replaying those events. There is no direct “mark verified” operation.

## State Boundary

The store accepts these events in order:

1. `run_created`
2. `work_started`
3. `executor_submitted`
4. `evaluation_recorded`
5. optional `work_retried` or `work_blocked`

An executor submission moves a work item only to `awaiting_audit`. A work item becomes `verified` only when a fingerprint-valid M03 evaluation report matches the work item and specification, all required evidence passes, and the report contains no protected regression.

Each JSONL event has a contiguous sequence number, the previous event hash, and its own SHA-256. Replaying a modified, reordered, missing, or malformed event fails. Dependency-ready work is derived only after every dependency is verified.

## Example API

```python
from pathlib import Path

from agentic_engineering.state_store import VerifiedStateStore

store = VerifiedStateStore(Path(".agent/state/run.jsonl"))
store.create(
    "run-1",
    "spec-1",
    [{"id": "implement", "depends_on": []}],
    "2026-08-15T20:00:00Z",
)
store.start("implement", "2026-08-15T20:01:00Z")
store.submit(
    "implement",
    ["src/change.py"],
    "Candidate is ready for independent evaluation.",
    "2026-08-15T20:02:00Z",
)
```

The caller then records a complete evaluation report from M03. Timestamps are explicit inputs so event replay is deterministic.

## Trust and Concurrency

The store validates report fingerprints and evidence consistency, but a hash chain is tamper-evident rather than an authentication signature. M05 separates the executor from the auditor that creates reports. The store remains intentionally single-writer; M09 provides isolated worktrees and integration rather than shared multi-process mutation.

## Promotion Gate

- Claims cannot verify work.
- Invalid transitions append nothing.
- Passing evidence verifies work and unlocks dependents.
- Failed evidence rejects work and permits an explicit retry.
- Forged or tampered records are rejected.
- Derived state and every event validate against their schemas.

## Test Command

```powershell
uv run --group test pytest
```

## Rollback

Revert the M04 store, event schema, tests, and documentation. Existing JSONL logs remain plain data and can be archived or removed separately.

## Next Module

[M05](05-verified-single-agent-runner.md) connects a manager, fresh executor, and read-only auditor around this state boundary.
