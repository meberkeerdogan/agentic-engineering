# Paper Dossier: SWE-Milestone

## Identity and review scope

- Local PDF: [`2603.13428-swe-milestone.pdf`](../../papers/2603.13428-swe-milestone.pdf)
- Manifest SHA-256: `ab1a668e7b7ba89399867479caca568faa65e3464c20cbb2fd5d2dc894f0cc8c`
- Version or date: arXiv v4, 2026-07-21; 46 pages
- Workflow section: long-task evaluation
- Review question: how should we measure error accumulation when an agent evolves the same repository through several dependent tasks?
- Relevant evidence: Sections 3-6; Tables 2-4; Figures 3-16 and 26-29; limitations; Appendices B-C

## Plain-English contribution

SWE-Milestone makes an agent build several features in the same repository, one after another. Earlier changes remain in place. This exposes a failure hidden by isolated tests: an agent can solve each feature separately but gradually damage the codebase when the work is continuous.

## Exact claims and evidence

- **Scale (direct):** 98 milestones across seven repositories, five languages, and 109 dependencies. A milestone averages 1,348 requirement words, changes 27.4 files, has 17.1 required-change tests, and is protected by 6,218 regression tests across the benchmark. Section 4.3.
- **Continuous result (direct):** the best reported Score is `38.03%` for Claude Opus 4.6 under OpenHands. The best full Resolve value in Table 2 is `13.37%` for Gemini 3 Pro, while the paper summarizes the frontier as roughly 13%. Table 2.
- **Independent-versus-continuous gap (direct):** per-repository isolated task scores are generally above 80%, but continuous scores are much lower. On scikit-learn, Claude Sonnet 4.6 scores `93.2%` independently and `21.1%` continuously. Figure 5 and Section 5.2.
- **Mechanism result (direct analysis):** required-feature recall continues to grow, but regression-control precision saturates. Later milestones and deeper dependency layers score worse. Figures 7-9.
- **Behavior result (direct association):** high edit repetition with little testing has the worst scores. Moderate, disciplined verification performs best; excessive verification or raw step count does not guarantee success. Figures 15-16.

## Method

- DeepCommit groups real commits into functionally coherent milestones and builds a dependency graph from code and history signals.
- An LLM drafts requirements by reading gold changes and tests; experts refine them to be complete without revealing implementation details.
- In continuous evaluation, an external scheduler unlocks a milestone only after prerequisites are submitted. The agent edits one persistent repository; each submission is snapshotted and tested in a separate container.
- Independent evaluation gives the same milestone the canonical starting code, removing accumulated agent errors.
- Recall is the fraction of required-change tests fixed. Precision is the fraction of all test-state changes that are fixes rather than regressions. Their harmonic mean is the primary Score. Full Resolve requires every target and regression test to pass.
- Fifteen agent-model configurations cover Claude Code, Codex CLI, Gemini CLI, and OpenHands. The unified prompt tells agents that prior work persists and submission is one-shot per milestone.

## Ablations and failure evidence

- Independent evaluation shows that many milestones are individually solvable, while continuous execution collapses. This is strong evidence that error accumulation matters.
- Later failures increasingly come from inherited or missing downstream behavior, not only new root mistakes.
- OpenHands sometimes spends far more time and turns without outperforming vendor tools. More retries are not automatically better.
- DeepCommit's dependency graph was compared with one human graph. It captures technical topology but can split a human-coherent cross-module goal into several phases.
- Root causes are assigned by an LLM reviewer that sees gold changes and evaluation artifacts; this is diagnostic, not the authoritative outcome metric.

## Limitations and transfer risks

- The benchmark requires rich executable tests and drops changes without useful dependency links. It favors dependency-heavy, well-tested work.
- Public repository history creates contamination risk.
- Humans still guide environment repair and requirement verification.
- Release ranges above roughly 30,000 changed lines exceed the current construction budget.
- The external scheduler means the paper evaluates work inside a provided plan. It does not show that giving any agent a dependency graph improves performance.
- Agentic Engineering's current roadmap fixture does not persist multiple agent-created milestones; it cannot measure snowballing regressions.

## Project transfer decision

- **Adopt:** compare the same milestones in isolated and continuous modes. Their difference directly measures error accumulation.
- **Adopt:** snapshot every milestone and score required progress separately from regressions.
- **Adapt:** start with short chains of 4-6 milestones and at least one branch-and-merge dependency, rather than reproducing all 98 milestones.
- **Adopt:** record inherited failures, healed failures, repeated edits, and test frequency as diagnostics.
- **Reject:** claiming that a dependency graph itself improves execution; it is part of benchmark delivery until tested as an intervention.

## Open questions

- How much of the continuous gap comes from one-shot milestone submission rather than persistence itself?
- Are the saturation-model projections stable beyond the seven evolution ranges?
- Which task-level recovery policy prevents inherited failures without creating excessive rework?
