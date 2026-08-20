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
- Deep-paper research gate: every workflow section now requires full primary-paper dossiers, cross-paper synthesis, explicit transfer decisions, and a predeclared evaluation. Completed sections with only design-level summaries are tracked for retrospective repair in the [section audit](research/WORKFLOW_SECTION_AUDIT.md).
- Core verification/specification review: LongHorizon-Harness supports separated execution and audit but has task-dependent cost and no clean component ablation; Progress Mirage supports matching evaluator access to where truth lives; SpecPath demonstrates path sensitivity but does not validate its proposed contract ledger. Review the [focused synthesis](research/reviews/core-workflow/SYNTHESIS.md).
- Optional Learning Companion boundary: a fresh teaching agent can now receive bounded milestone evidence and return a lesson proposal without verification or engineering-mutation authority. Review [M10](docs/modules/10-learning-companion.md).

## Current topic

Finish the remaining core baseline/decomposition papers, then repair memory and long-task evaluation in sequence.

## Current exercise

Why is the current active-spec compiler an adaptation rather than a SpecPath reproduction?

**Answer:** SpecPath tests agents reading natural-language histories across 1,470 planned executions. Our compiler receives already-structured revision operations and deterministically compiles them. It implements a proposed ledger idea, but it neither performs the paper's inference task nor reproduces its benchmark.

## Suggested next topics

1. Core baseline and decomposition dossiers: Agentless and Runtime-Structured Task Decomposition.
2. Memory dossiers and retrospective phase-memory alignment audit.
3. Long-task benchmark validity and harder task design.
4. Ceiling effects and predeclared efficiency hypotheses.

## Milestone report checklist

Every meaningful-stage report should explain the concepts, selected approach and alternatives, result interpretation, one exercise, and review questions. Keep the review surface focused and preserve lessons from failed experiments.
