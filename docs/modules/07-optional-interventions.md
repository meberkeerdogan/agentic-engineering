# M07: Optional Interventions

**Status:** In progress — observe-only watchdog and calibration implemented

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

The [M06h live capture bridge](06h-live-trajectory-capture.md) now produces the redacted per-cell trajectories needed for this calibration work.

### Calibration workflow

`watchdog_calibration` binds each label set to the exact fingerprinted watchdog report. Every detected signal must receive exactly one true-positive or false-positive label, while reviewer-found misses are recorded as false negatives. Duplicate cases and duplicate missed windows are rejected so support cannot be inflated.

The calibration report calculates precision, recall, and false-positive rate for all five signal types. A signal becomes eligible for an advisory experiment only when it reaches the predeclared minimum support, precision, and recall. Eligibility does not enable advice; every calibration report remains `calibration_only` with an empty `interventions` array.

```powershell
uv run python -m agentic_engineering.watchdog_calibration `
  examples/watchdog-calibration.json `
  --output watchdog-calibration-report.json
```

The bundled labels are a deterministic fixture, not performance evidence. The default policy requires at least five labels per signal type, so the one-case fixture is ineligible unless its explicit test-only threshold is used.

### First live calibration cases

The [representative sentinel dataset](../../research/calibration/representative-sentinel-001/) adds two real, privacy-safe cases. Both arms triggered `premature_patching`, but both declared workflows intentionally test after implementation and both independent audits passed. Human review therefore labels both alerts false positives for this context.

With two false positives and the predeclared minimum of five labels, `premature_patching` has zero precision on this small dataset and remains ineligible for an advisory experiment. This does not establish its general quality; it establishes that workflow-aware calibration is required before advice.

The multi-step evolution sentinel adds two more contextual false positives. The combined live manifest now contains four fingerprint-bound cases, still below the five-label support threshold, with no eligible advisory signal and no interventions.

## M07b: Calibration-Gated Advice

`advisory_watchdog` converts observe-only signals into deterministic messages only when the exact fingerprinted calibration report marks that signal type eligible. Tampered reports, inconsistent eligibility, and unsupported signals fail closed. Advice is delivered only at a declared safe boundary; the output has structurally empty intervention and blocking arrays.

The synthetic fixture proves the mechanism. The combined real calibration currently permits no signal types, so real sentinel reports produce zero advice. M07b is implemented but not promoted as a default behavior.

## Remaining M07 Slices

- M07c: static versus adaptive dependency planning.
- M07d: phase-aware memory.
- M07e: complementary agentic property testing.

Each slice will be implemented and promoted independently.
