# M07: Optional Interventions

**Status:** In progress — M07a observe-only watchdog implemented

## Why This Module Is Split

Planning, memory, property testing, reminders, and watchdog advice are different interventions. Bundling them would make any improvement impossible to attribute. Each intervention therefore becomes its own experiment arm and must pass a target-specific M06 comparison before it can become a default.

## M07a: Observe-Only Watchdog

The first slice implements deterministic trajectory monitoring inspired by [LivePlan](../../research/papers/2608.06701-liveplan.pdf) and constrained by the false-progress findings in [Progress Mirage](../../research/papers/2607.25152-progress-mirage.pdf).

It detects five candidate signals from recorded events:

- repeated actions on the same target;
- unchanged external state over a configured event window;
- two-action oscillation;
- patching before reproduction;
- claiming completion after a patch without later validation.

The output is always `observe_only` and its `interventions` array is always empty. Signals are labelled as advisory or blocking candidates, but the watchdog does not send advice, stop an agent, retry work, or change state.

Every event has a supported phase, a strictly increasing step, an external state fingerprint, and evidence references. Thresholds and a fingerprint of the complete source trajectory are explicit in the report, and identical trajectory/config inputs produce the same fingerprinted output.

## Run the Fixture

```powershell
uv run python -m agentic_engineering.watchdog `
  examples/watchdog-trajectory.json `
  --output watchdog-report.json
```

## M07a Promotion Gate

- Golden and repeated reports are deterministic.
- A healthy reproduce-patch-validate trajectory produces no signals.
- Repeated action, stagnation, oscillation, premature patching, and skipped validation are detected from evidence.
- Invalid order and invalid thresholds fail.
- No code path can advise, block, or mutate the source trajectory.

## Before Advice or Blocking

Collect watchdog reports on control trajectories, label true and false alarms, and use M06 to compare an advisory treatment against observation-only control. Blocking is eligible only if it improves verified completion without unacceptable regressions, false interventions, cost, or time.

## Remaining M07 Slices

- M07b: calibrated advisory watchdog.
- M07c: static versus adaptive dependency planning.
- M07d: phase-aware memory.
- M07e: complementary agentic property testing.

Each slice will be implemented and promoted independently.
