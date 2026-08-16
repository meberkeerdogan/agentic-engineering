# M06e: Resumable Batch Experiment Runner

**Status:** Implemented

## Purpose

The batch runner executes a complete control/treatment matrix in small, durable chunks. A long experiment can stop between cells and continue later without repeating completed work or losing its accumulated cost, time, intervention, and evaluation evidence.

## How it works

The committed batch configuration declares the experiment, storage location, cost unit, total ceilings, per-run ceilings, and the number of cells allowed in one invocation. Before the first adapter runs, the runner verifies that the budgets can reserve the entire worst-case matrix. Adapter launchers can also bind an execution fingerprint so changed prompts, templates, rate cards, or other execution inputs cannot be mixed into a resumed batch.

For every cell, the runner atomically records `running` before calling the adapter and records the validated observation afterward. A lock prevents two processes from executing the same batch concurrently. The plan and configuration fingerprints prevent a resume from silently changing the experiment.

Completed cells are never called again. Once every cell is complete, the stored observations are replayed through the existing deterministic M06 report builder. The resulting `experiment-report.json` contains the same deterministic report data as a one-shot run over the same observations.

## Failure boundaries

- Adapter error messages are not persisted because they may contain private output; only the exception type is stored.
- A cell that exceeds a declared per-run limit fails closed, while its measured spend remains in state.
- Changed plans, changed budgets, inconsistent totals, altered reports, filesystem links, and missing state are rejected.
- If a process dies while a paid cell is marked `running`, the runner does not automatically repeat it. First reconcile whether the external agent completed and what it spent, then repair or replace the cell evidence deliberately.
- A forcibly killed process can leave `batch.lock`. Verify that no runner is active before removing that one lock file.

## Offline example

The example deliberately allows two of four cells per invocation:

```powershell
uv run python -m agentic_engineering.batch_experiments examples/batch-experiment.json examples/experiment-observations.json
```

The first call returns `paused` at 2/4. Run the same command again to finish at 4/4 and create the report. This replay command spends no credits. Real Codex integration uses the same `run_experiment_batch` API with M06b adapters and must apply the M06d preflight before each model execution.

## Contracts

- [`batch-experiment.schema.json`](../../schemas/batch-experiment.schema.json) defines immutable budgets and references.
- [`batch-state.schema.json`](../../schemas/batch-state.schema.json) defines the resumable ledger.
- [`expected-batch-state.json`](../../examples/expected-batch-state.json) is the golden paused checkpoint.

Private batch state belongs under ignored `.agentic-runs/` storage and should not be committed.

For real Codex control/treatment cells with a fresh preflight before each call, see [M06f: Live Codex Experiment Bridge](06f-live-codex-experiments.md).
