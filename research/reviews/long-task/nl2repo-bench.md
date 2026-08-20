# Paper Dossier: NL2Repo-Bench

## Identity and review scope

- Local PDF: [`2512.12730-nl2repo-bench.pdf`](../../papers/2512.12730-nl2repo-bench.pdf)
- Manifest SHA-256: `a56b714df3cb3d3e68ac57cff048fa16868ecb9788e57a94828253f6cab4e0e6`
- Version or date: arXiv v2, 2026-01-08; 25 pages
- Workflow section: long-task evaluation
- Review question: what can full repository generation teach us about long-task failure and product acceptance testing?
- Relevant evidence: Sections 3-5; Tables 1-8; Figures 3-9; benchmark-construction appendices

## Plain-English contribution

NL2Repo-Bench gives an agent a long requirements document and an empty folder. The agent must create a complete installable Python library without seeing the source repository or tests. This tests architecture, packaging, dependencies, multi-file consistency, and persistence, but it is a different job from evolving an existing project.

## Exact claims and evidence

- **Scale (direct):** 104 Python-library tasks in nine categories. Specifications average about 18,800 tokens. Easy, medium, and hard bands contain 26, 46, and 32 tasks based on source-repository size. Tables 1-2.
- **Main result (direct, apparently one run):** Claude Sonnet 4.5 under Claude Code has the best average test score at `40.2%` and fully passes 3 of 104 tasks. Claude Sonnet 4 under OpenHands fully passes the most tasks, 5, despite a lower `37.0%` average. Table 3.
- **Difficulty result (direct):** the top system falls from `51.8%` on easy tasks to `25.1%` on hard tasks. Table 3.
- **Hidden-test ablation (direct):** showing all upstream tests raises Claude Sonnet 4.5 from `40.2%` to `59.4%` and full passes from 3 to 18, but still leaves substantial failure. Table 8.
- **Step-budget ablation (direct):** performance rises strongly from 50 to 200 rounds, then mostly saturates. Figure 9.
- **Internal reporting issues:** the conclusion says the leading pass rate is `39.6%`, while Table 3 reports `40.2%`. Table 6 reports DeepSeek V3.2 at `22.2%`, while Table 3 reports `27.6%`.

## Method

- Repositories are recent Python libraries with 300-120,000 lines, at least 10 stars, and a passing pytest suite.
- Human annotators reverse-engineer the source and tests into a project description, dependency and directory guidance, API guide, and detailed implementation nodes.
- AST tools check that public functions, classes, signatures, and semantics are covered. Experts and preliminary agent runs find missing or ambiguous requirements.
- Each agent starts in an empty workspace with only the specification and no iteration limit. The final repository is placed in a Docker image and evaluated with modified upstream pytest execution that continues past collection failures.
- The primary score is the average fraction of upstream tests passed; Pass@1 counts repositories whose entire suite passes.

## Ablations and failure evidence

- Extra rounds stop helping much beyond roughly 200, so unlimited effort does not solve architectural and semantic failures.
- Showing hidden tests materially helps but does not raise the score above 60%.
- Common failures include missing package structure, broken imports, API mismatch, early completion claims, waiting for user input, navigation loops, and long blind-edit sequences.
- Tool-planning frequency correlates with score, but this is an across-model association, not a causal planning ablation.
- The paper claims framework choice matters little for Claude Sonnet 4.5, but only three closely related framework runs are compared and results are single-run.

## Limitations and transfer risks

- The paper has no dedicated limitations or threats-to-validity section.
- Specifications are reverse-engineered from source code and tests. They may be more complete and API-specific than ordinary product requirements.
- Public repositories and tests create contamination risk, which the paper does not quantify.
- Average test pass rate can be dominated by numerous easy tests and does not apply a strict regression concept because the workspace starts empty.
- “Early termination” is defined partly as finishing before 100 turns. A short correct run would also meet that timing rule, so timing alone is not a correctness signal.
- Empty-workspace generation is outside the main Agentic Engineering v0.1 use case of improving work in existing repositories.

## Project transfer decision

- **Adopt:** include installability, packaging, internal imports, and end-to-end use in the v0.1 acceptance example.
- **Adopt:** independently reject premature completion and unfinished runs.
- **Adapt:** use a small empty-workspace smoke test only after the existing-repository workflow is usable.
- **Reject:** using average test pass rate alone for project evolution; preserve strict regression measures there.
- **Defer:** a complete NL2Repo reproduction because it tests a different product mode and is expensive.

## Open questions

- Are reported results repeated or single-run, and what is their variance?
- How much of the score is recoverable from public package memorization?
- How does the modified pytest collection procedure weight repositories with many collection failures?
