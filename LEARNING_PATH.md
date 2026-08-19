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
- Phase-memory live campaign evidence: all nine controls, all three low-pressure treatments, and the complete three-seed supersession block passed with zero regressions, false completions, or human interventions. The campaign is at `15 / 18`; review the complete restock comparison in [cell 15](research/reports/2026-08-19-phase-memory-campaign-cell-15.md). Memory reliably excluded the obsolete decision; treatment quality was equal, cost was `0.14%` higher, and time was `11.36%` lower.
- Optional Learning Companion boundary: a fresh teaching agent can now receive bounded milestone evidence and return a lesson proposal without verification or engineering-mutation authority. Review [M10](docs/modules/10-learning-companion.md).

## Current topic

Run the three eviction-pressure roadmap treatments, then apply the predeclared promotion rule to the complete campaign.

## Current exercise

What did the completed restock block prove, and what did it not prove?

**Answer:** it proved that bounded memory consistently filtered the obsolete decision without causing errors and was faster overall at almost identical cost. It did not prove a completion benefit because all controls also passed. Correct mechanism behavior is not the same as improved task outcomes.

## Suggested next topics

1. Eviction pressure through the multi-step `roadmap-evolution` task.
2. Compare supersession and eviction results against the low-pressure block.
3. Paired control/treatment comparisons, effect size, and uncertainty.
4. Applying the predeclared promotion rule without changing it after seeing results.
5. Connecting a runtime-specific teaching-agent adapter and evaluating lesson quality, context saved, cost, and time.

## Milestone report checklist

Every meaningful-stage report should explain the concepts, selected approach and alternatives, result interpretation, one exercise, and review questions. Keep the review surface focused and preserve lessons from failed experiments.
