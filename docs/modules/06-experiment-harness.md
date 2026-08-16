# M06: Experiment Harness

**Status:** Implemented

## Why This Module Exists

An intervention should not become a default because one run looked good. This module runs a fixed control/treatment matrix over declared tasks and seeds, then reports verified completion, regressions, false completion, cost, time, and human intervention.

The design follows the project research review:

- [Progress Mirage](../../research/papers/2607.25152-progress-mirage.pdf) motivates deriving false completion from an agent claim plus external verification instead of trusting self-reported progress.
- [Evaluating AGENTS.md](../../research/papers/2602.11988-evaluating-agents-md.pdf) motivates measuring cost alongside success because an intervention can increase work without improving outcomes.
- [SWE-EVO](../../research/papers/2512.18470-swe-evo.pdf), [RoadmapBench](../../research/papers/2605.15846-roadmapbench.pdf), and [SWE-Milestone](../../research/papers/2603.13428-swe-milestone.pdf) motivate multi-task, repeated evaluation with regression-sensitive measures.

## Fixed Experiment Matrix

The experiment record declares the control, treatments, tasks, seeds, exact standard metric set, and adoption rule before execution. `run_experiment` rejects prior run data, duplicate identifiers, missing or unsupported metrics, and adapter registrations that do not exactly match the declared arms.

Each adapter receives one arm, task, and seed. It returns an externally measured `RunObservation`. The harness derives false completion itself as:

```text
claimed complete AND not verified complete
```

Every observation needs an evidence reference. Cost and time are supplied by the adapter rather than measured inside the harness so integrations can use their authoritative provider, token, and wall-clock records.

Production adapters must run every cell from the same declared repository revision in a fresh, isolated workspace. The harness fixes and validates the matrix; the adapter owns environment isolation and authoritative measurement.

## Output

The report contains:

- every planned arm/task/seed run in deterministic order;
- per-arm completion rates, regression counts, false-completion rates, mean cost, mean time, and human intervention totals;
- paired treatment-minus-control deltas;
- cost per additional verified completion when the treatment has a positive completion gain;
- a content fingerprint and deterministic report ID;
- the adoption rule and a fingerprint of the exact predeclared plan.

The replay adapter and example observation file make the harness testable without invoking an external coding agent.

For longer matrices, the [M06e resumable batch runner](06e-resumable-batch-runner.md) stores each validated observation atomically, enforces declared budgets, and feeds the complete stored matrix back through this same deterministic report builder.

## Run the Example

```powershell
uv run python -m agentic_engineering.experiments `
  examples/experiment-record.json `
  examples/experiment-observations.json `
  --output experiment-report.json
```

The small repository fixture proves determinism. A decision-quality experiment should follow the research protocol: use at least two repositories, include bounded and multi-step tasks, and run multiple seeds per arm.

## Promotion Gate

- Repeated execution of the same fixed inputs is byte-stable.
- Missing cells, duplicate cells, incomplete metrics, and unevidenced observations fail.
- False completion is derived independently from claim and verification fields.
- The golden report includes completion, regression, false-completion, cost, time, and intervention summaries plus paired deltas.

## Rollback

Revert the M06 harness, report/replay schemas, examples, tests, and documentation. M01–M05 remain independently usable.

## Next Module

M07 is adding optional interventions one at a time, beginning with an observe-only trajectory watchdog. Behavioral interventions must beat this experiment baseline on their declared target.
