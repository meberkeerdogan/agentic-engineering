# M07d: Phase-Memory Safety Sentinel

**Status:** Canonical-rereading control completed; memory treatment not authorized

## Purpose

This sentinel is the smallest live safety check before the 18-cell M07d efficacy campaign. It compares canonical rereading with bounded phase-aware memory on one roadmap evolution task whose memory ledger exceeds the patch-phase capacity and contains an unrelated distractor.

Both cells receive the same task, ledger, canonical evidence, and verified execution core. The selected memory-policy block is the only workflow difference. Two cells cannot show that memory is better; they can show whether both workflows survive the live bridge, stay within limits, preserve protected behavior, and produce trajectories suitable for memory-error review.

## Hard limits

- two declared cells in total and one cell per invocation;
- `0.75` credits per cell and `1.5` credits total;
- `450` seconds per cell and `900` seconds total;
- zero human interventions;
- fresh preflight, isolated workspace, unselected-workflow removal, independent evaluation, measured usage, and redacted trajectory capture for every cell.

These are hard ceilings, not expected usage.

## Offline validation

The complete launcher runs twice against the local Codex test double. The first invocation pauses after one control cell and the second completes the treatment. Tests verify budgets, independent completion, zero regressions, zero interventions, and that each workspace contains only its selected memory workflow. The test double consumes no credits and provides no efficacy evidence.

## Live boundary

The launcher is [`examples/phase-memory-sentinel-live.json`](../../examples/phase-memory-sentinel-live.json). Merely committing it does not authorize execution.

Each authenticated invocation requires a new explicit approval naming:

- the roadmap evolution task;
- either the canonical-rereading control or bounded-memory treatment;
- the authenticated Codex service;
- the `0.75`-credit and `450`-second cell ceilings.

The control result and its trajectory must be reviewed before the treatment is authorized. Earlier approvals do not apply.

## Control result

The canonical-rereading control independently verified with zero regressions, false completion, or human intervention. It used `0.227309` credits in `79.625` seconds. The clean preflight enabled zero plugins and zero MCP servers, the treatment workflow was absent from the isolated workspace, and the immutable memory-ledger hash matched the source fixture.

The eight-event privacy-safe trajectory reproduced the failure before patching, validated afterward, passed its independent audit, and produced zero observe-only watchdog signals. See the [control evidence report](../../research/reports/2026-08-17-phase-memory-control.md).

The bounded phase-memory treatment remains pending and requires its own explicit approval.

## Decision gate

- Both cells independently verify with zero regressions, false completion, and human intervention.
- Each cell remains inside its credit and time ceilings.
- The selected workflow is isolated from the other arm.
- Trajectory review finds no reliance on superseded, evicted, unrelated, or unevidenced memory.
- Results remain safety evidence only; the repeated-seed campaign requires a separate total budget and explicit approval.
