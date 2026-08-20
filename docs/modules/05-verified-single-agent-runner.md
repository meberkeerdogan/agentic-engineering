# M05: Verified Single-Agent Runner

**Status:** Implemented

## Why This Module Exists

The state and evaluator layers become useful when execution and judgment are kept separate. This module coordinates one bounded work item through a manager, a fresh executor, and an independent auditor.

The detailed [LongHorizon-Harness dossier](../../research/reviews/core-workflow/longhorizon-harness.md) supports this separation as a promising architecture, with task-dependent benefits and substantial possible overhead. M05 is a smaller **adaptation**, not a reproduction: its manager is deterministic, its work items are predeclared, and it does not run the paper's repeated LLM Manage-Execute-Audit rounds. See the [core synthesis](../../research/reviews/core-workflow/SYNTHESIS.md).

## Roles

- The **manager** reads verified state, starts only a ready item, creates the execution request, and controls transitions.
- The **executor** receives only run/spec/work identifiers and an attempt number. It can return artifact references, a completion claim, and a revision identifier. It cannot return evidence or a state transition.
- The **auditor** receives the submitted artifacts and revision, then returns a complete M03 evaluation report.

The manager rejects a factory that reuses an executor object or returns the auditor itself. A new executor is therefore required on every retry. Invalid executor output blocks the item without evidence. Auditor or report failures also block rather than verify it.

## Built-In Auditor

`SinglePassAuditor` connects a trusted evidence contract and evaluation root to the deterministic M03 baseline. Custom executors and auditors can implement the small Python protocols in `agentic_engineering.runner`. Evaluators must declare themselves read-only, but command evaluators are not yet isolated by an operating-system read-only sandbox; the declaration is a trust contract rather than proof of non-mutation.

## Promotion Gate

- A normal executor submission plus passing independent audit verifies the item.
- A failing audit rejects the item; retry constructs a distinct executor.
- An executor cannot smuggle its own evaluation report through the submission type.
- A mismatched audit contract blocks the item with no evidence.
- A cached executor is rejected on retry.

## Test Command

```powershell
uv run --group test pytest
```

## Rollback

Revert the M05 runner, tests, and documentation. M03 evaluators and M04 logs remain independently usable.

## Next Module

M06 now runs repeatable control/treatment comparisons and aggregates completion, regression, false-completion, cost, time, and intervention metrics.
