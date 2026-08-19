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
- Phase-memory live campaign evidence: all nine controls and the first bounded-memory treatment passed with zero regressions, false completions, or human interventions. The campaign is at `10 / 18`; review the first paired comparison in [cell 10](research/reports/2026-08-19-phase-memory-campaign-cell-10.md). Treatment quality was equal, cost was `6.77%` higher, and time was `2.99%` lower.
- Optional Learning Companion boundary: a fresh teaching agent can now receive bounded milestone evidence and return a lesson proposal without verification or engineering-mutation authority. Review [M10](docs/modules/10-learning-companion.md).

## Current topic

Run the remaining eight bounded phase-memory treatment cells and compare each task and seed with the complete canonical-rereading baseline.

## Current exercise

What does the first median pair tell us, and why is it not enough to judge phase memory?

**Answer:** both workflows completed correctly. Treatment cost `6.77%` more but finished `2.99%` faster. This is one low-pressure pair, so normal run-to-run variation may explain the differences; repeated seeds and the pressure tasks are still required.

## Suggested next topics

1. Supersession pressure through the multi-file `restock-report` task.
2. Eviction pressure through the multi-step `roadmap-evolution` task.
3. Paired control/treatment comparisons, effect size, and uncertainty.
4. Applying the predeclared promotion rule without changing it after seeing results.
5. Connecting a runtime-specific teaching-agent adapter and evaluating lesson quality, context saved, cost, and time.

## Milestone report checklist

Every meaningful-stage report should explain the concepts, selected approach and alternatives, result interpretation, one exercise, and review questions. Keep the review surface focused and preserve lessons from failed experiments.
