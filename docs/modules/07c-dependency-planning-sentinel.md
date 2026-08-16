# M07c: Dependency-Planning Safety Sentinel

**Status:** Prepared and offline-validated; authenticated cells not authorized

## Purpose

This sentinel is the smallest live safety check before the 18-cell M07c efficacy campaign. It compares the static-plan control with the adaptive-plan treatment on the diamond-shaped roadmap evolution task using one seed. The marked planning-policy block is the only workflow difference; both arms retain the same verified execution core.

Two cells cannot show that adaptive planning is better. They can show whether both workflows survive the live bridge, stay within limits, preserve protected behavior, and produce independent evidence suitable for review.

## Hard limits

- two declared cells in total and one cell per invocation;
- `0.75` credits per cell and `1.5` credits total;
- `450` seconds per cell and `900` seconds total;
- zero human interventions;
- fresh preflight, isolated workspace, unselected-workflow removal, independent evaluation, usage evidence, and redacted trajectory capture for every cell.

These are hard ceilings, not expected usage.

## Offline validation

The complete launcher ran twice against the local Codex test double. The first invocation paused after one cell and the second completed the matrix. Tests verify the budgets, independent completion, zero regressions, zero interventions, and that each isolated workspace contains only its selected static or adaptive planning workflow. The test double consumes no credits and provides no efficacy evidence.

## Live boundary

The launcher is [`examples/dependency-planning-sentinel-live.json`](../../examples/dependency-planning-sentinel-live.json). Merely committing it does not authorize execution.

Each authenticated invocation requires a new explicit approval naming:

- the roadmap evolution task;
- either the static control or adaptive treatment arm;
- the authenticated Codex service;
- the `0.75`-credit and `450`-second cell ceilings.

The control result must be independently reviewed before the treatment cell is authorized. Earlier approvals for other sentinels do not apply.

## Decision gate

- Both cells must independently verify with zero regressions, false completion, and human intervention.
- Each cell must remain inside its credit and time ceilings.
- The selected workflow must be isolated from the other arm.
- Trajectory evidence must remain privacy-safe and observe-only.
- Results remain safety evidence only; the repeated-seed campaign still requires a separate total budget and explicit approval.
