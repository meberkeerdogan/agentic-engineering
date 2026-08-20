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
- Core baseline/decomposition review: Agentless establishes that complex agents must beat a cheap fixed pipeline; RSTD shows selective retry can reduce injected-failure recovery cost, while decomposition adds normal overhead and did not improve correctness in its two cases.
- Memory review and implementation audit: Prometheus caches repository evidence, ContextBench shows that broad retrieval can add noise, and PMCoder couples episodic recall with planning and recovery. Our bounded phase ledger is a safer project-memory adaptation, not a reproduction. Its `9/9` versus `9/9` campaign remains a useful negative result.
- Optional Learning Companion boundary: a fresh teaching agent can now receive bounded milestone evidence and return a lesson proposal without verification or engineering-mutation authority. Review [M10](docs/modules/10-learning-companion.md).

## Current topic

Turn the completed core modules into one simple `v0.1` product workflow. Long-task paper review remains the next research stage, but it does not block product use.

## Current exercise

What is the difference between a completed engine and a usable product?

**Answer:** the engine contains the working parts, tests, and internal commands. A usable product gives a new user one clear setup, one supported command, understandable output, and an example that works from a fresh checkout.

## Suggested next topics

1. Freeze the supported `v0.1` workflow and user journey.
2. Add one simple product command and end-to-end example.
3. Resume long-task benchmark research as a separate track.
4. Add retrieval-quality instrumentation only before another memory experiment.

## Milestone report checklist

Every meaningful-stage report should explain the concepts, selected approach and alternatives, result interpretation, one exercise, and review questions. Keep the review surface focused and preserve lessons from failed experiments.
