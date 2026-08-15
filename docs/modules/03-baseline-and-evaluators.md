# M03: Baseline and Evaluators

**Status:** Implemented

## Why This Module Exists

Later agent workflows need a control condition and evidence that does not depend on the agent judging its own work. This module runs a prepared candidate through declared evaluators exactly once. It makes no agent calls, generates no repair, and performs no retry loop.

This is an agentless-style control harness, not a reproduction of the complete Agentless paper. Repair generation and agent adapters belong in later experiments.

## Evaluators

| Type | What it observes |
| --- | --- |
| `command` | An argument-array command, executed without a shell, compared with an expected exit code |
| `artifact` | A repository-local file's presence, size, and optional SHA-256 |
| `rubric` | Weighted assertions over a JSON artifact, compared with a declared threshold |
| `world_state` | Required assertions over an independently observed JSON state artifact |

All four implementations return the same deterministic result shape. Required criterion results and protected baseline regressions are then derived into an `evaluation-report` document. Wall-clock times and absolute machine paths are deliberately excluded from the report fingerprint.

## Example

```powershell
uv run python -m agentic_engineering.evaluators examples/fixture-task/evidence-contract.json `
  --root examples/fixture-task `
  --output evaluation.json
```

The committed fixture report is byte-stable across repeated runs and validates against `schemas/evaluation-report.schema.json`.

## Trust Boundary

Artifact paths are constrained to the evaluation root, and commands use argument arrays with `shell=False`. However, `read_only: true` is a contract assertion, not an operating-system sandbox. Run command evaluators only from trusted evidence contracts. A later isolation module can add stronger process and filesystem containment.

## Promotion Gate

The fixture must produce exactly `examples/fixture-task/expected-evaluation.json`. All four evaluator types must pass, repeated runs must match, and a failing protected command must be reported as both failed evidence and a regression.

## Test Command

```powershell
uv run --group test pytest
```

## Rollback

Revert the M03 evaluator code, expanded evidence schema, evaluation-report schema, fixture, tests, and documentation. The runner writes only an explicitly requested report file.

## Next Module

[M04](04-verified-state-store.md) uses these reports to drive an append-only verified-state store. Claims alone cannot advance a work item to verified.
