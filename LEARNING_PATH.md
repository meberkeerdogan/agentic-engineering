# Learning Path

This file is a short map of what the project has taught, what is being tested now, and what to study next. Update it only after meaningful milestones.

## Key vocabulary

- **Verified completion:** independent checks accept the result; the agent's own completion claim is not enough.
- **Control:** the simpler existing workflow used as the comparison baseline.
- **Treatment:** the new method being tested against the control.
- **Promotion gate:** evidence required before an experimental method becomes a default.
- **Negative result:** an experiment that did not show an improvement. It is preserved because it prevents unsupported decisions and guides the next experiment.

## Completed topics

- Agentic engineering as a complete system around an agent, not only a prompt, loop, or skill. Review [the implementation plan](docs/implementation-plan.md).
- Active specifications, evidence contracts, verified state, fresh executors, and independent auditors. Review the focused [module map](docs/modules/README.md).
- Controlled and resumable experiments with isolated workspaces, hard budgets, repeated seeds, and external evaluation.
- Failed or inconclusive interventions as useful evidence: adaptive planning did not beat its sentinel control; early watchdog alerts were contextual false positives; the two-cell phase-memory sentinel established safety but not efficacy.
- Phase-memory live campaign evidence: 17 of 18 cells passed with zero regressions, false completions, or human interventions. Both eviction treatments removed the unrelated distractor. Review [cell 17](research/reports/2026-08-20-phase-memory-campaign-cell-17.md): seed `0` favored treatment, seed `1` favored control, and their aggregate is nearly equal in cost and time.
- Optional Learning Companion boundary: a fresh teaching agent can now receive bounded milestone evidence and return a lesson proposal without verification or engineering-mutation authority. Review [M10](docs/modules/10-learning-companion.md).

## Current topic

Run the final eviction-pressure roadmap treatment, aggregate all 18 cells, and apply the predeclared promotion rule.

## Current exercise

Why did the second roadmap result change our interpretation of the first?

**Answer:** seed `0` made treatment look cheaper and faster, while seed `1` made it look more expensive and slower. Both had equal quality and correct eviction. Combining them leaves almost no efficiency difference, demonstrating that a single favorable run can be ordinary variation rather than a workflow effect.

## Suggested next topics

1. Eviction pressure through the multi-step `roadmap-evolution` task.
2. Compare supersession and eviction results against the low-pressure block.
3. Paired control/treatment comparisons, effect size, and uncertainty.
4. Applying the predeclared promotion rule without changing it after seeing results.
5. Connecting a runtime-specific teaching-agent adapter and evaluating lesson quality, context saved, cost, and time.

## Milestone report checklist

Every meaningful-stage report should explain the concepts, selected approach and alternatives, result interpretation, one exercise, and review questions. Keep the review surface focused and preserve lessons from failed experiments.
