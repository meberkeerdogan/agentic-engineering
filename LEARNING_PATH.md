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
- Phase-memory live campaign evidence: all 18 cells independently verified with zero regressions, false completions, memory-attributable errors, or human interventions. Review the [final report](research/reports/2026-08-20-phase-memory-campaign-cell-18.md). Memory behaved correctly, but both arms completed `9 / 9`; treatment cost `5.51%` more and took `6.93%` less time overall. The required completion improvement was absent, so default promotion was rejected.
- Optional Learning Companion boundary: a fresh teaching agent can now receive bounded milestone evidence and return a lesson proposal without verification or engineering-mutation authority. Review [M10](docs/modules/10-learning-companion.md).

## Current topic

Interpret the completed null result and design a harder replication where the baseline does not already achieve perfect completion.

## Current exercise

Should bounded phase memory become the default after this campaign?

**Answer:** no. It was safe, correctly filtered memory, and ran faster overall, but it did not improve verified completion over the simpler baseline and cost more overall. The predeclared rule required a completion gain, so changing the rule after seeing the results would be research bias.

## Suggested next topics

1. Ceiling effects: why a perfect baseline prevents measuring completion improvement.
2. Design harder, longer memory-pressure tasks across more repositories and models.
3. Predeclare an efficiency hypothesis and increase repeated-run support.
4. Connect a runtime-specific teaching-agent adapter and evaluate lesson quality, context saved, cost, and time.

## Milestone report checklist

Every meaningful-stage report should explain the concepts, selected approach and alternatives, result interpretation, one exercise, and review questions. Keep the review surface focused and preserve lessons from failed experiments.
