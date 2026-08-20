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
- Long-task evaluation review: release-sized and continuous benchmarks show that partial progress is common, regressions accumulate, and isolated successes often fail to compose. Our three small tasks are valid safety fixtures but too easy for efficacy claims. Review the [synthesis](research/reviews/long-task/SYNTHESIS.md) and [harder test design](research/reviews/long-task/HARDER_TEST_DESIGN.md).
- Regression-safe target scoring: harder evidence contracts can group criteria by target. Reports preserve the raw fraction completed, while the strict score becomes zero if protected old behavior breaks. Review `run_single_pass_baseline` in [evaluators.py](agentic_engineering/evaluators.py).
- Level 1 task validation: a 749-line project now has five named upgrade targets, visible checks, hidden checks, and an external oracle. The untouched project scores `0/5` without regressions; the oracle scores `5/5`. Review [M06k](docs/modules/06k-long-task-level-1.md).
- Level 2 continuous validation: five milestone oracles now pass both alone and in one persistent repository, while intentionally omitting Milestone 1 creates a later protected regression. Review [M06l](docs/modules/06l-long-task-level-2.md).
- Optional Learning Companion boundary: a fresh teaching agent can now receive bounded milestone evidence and return a lesson proposal without verification or engineering-mutation authority. Review [M10](docs/modules/10-learning-companion.md).
- `v0.1` feature freeze: the supported product is now the verified single-agent workflow. Technically working but unproven interventions remain explicit experiments rather than hidden defaults. Review the [product scope](docs/v0.1-product-scope.md) and [frozen workflow](workflows/verified-single-agent-v0.1.md).
- Product boundary and interface: one deep Python function now powers both the command line and a local browser UI. The UI improves usability without duplicating verification logic or enabling experimental features. Review [product.py](agentic_engineering/product.py), [ui.py](agentic_engineering/ui.py), and the [Getting Started guide](docs/getting-started.md).

## Current topic

Run the supported product from a clean checkout and fix only problems that block first use or trustworthy output.

## Current exercise

Why should the command line and UI call the same workflow function?

**Answer:** one shared function keeps safety checks, evidence, and results consistent. Two separate implementations could drift and make the UI appear successful when the command line would reject the same run.

## Suggested next topics

1. Run the fresh-checkout acceptance test and fix release blockers.
2. Prepare the `v0.1.0` tag, package, and release notes.
3. Test the prepared-project setup with a user who did not build the system.
4. Keep held-out agent evaluations and new methods in the post-release research backlog.

## Milestone report checklist

Every meaningful-stage report should explain the concepts, selected approach and alternatives, result interpretation, one exercise, and review questions. Keep the review surface focused and preserve lessons from failed experiments.
