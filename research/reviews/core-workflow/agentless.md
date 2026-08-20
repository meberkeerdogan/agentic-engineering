# Paper Dossier: Agentless

## Identity and review scope

- Local PDF: [`2407.01489-agentless.pdf`](../../papers/2407.01489-agentless.pdf)
- Manifest SHA-256: `1675c2dcd5ecaef47e8a4356062f60be642cee82e1bbacb044c9d047dce4c856`
- Version or date: arXiv v2, 2024-10-29; reviewed 2026-08-20
- Workflow section: core verified workflow, simpler baseline
- Review question: can a fixed staged pipeline provide a competitive, cheaper baseline that complex coding-agent workflows must beat?
- Relevant evidence: Sections 3-8; Tables 1-6; Figures 1, 5-9; component ablations and validity threats

## Plain-English contribution

Agentless does not let an LLM freely choose tools or its next action. Code fixes pass through a fixed pipeline: narrow the repository to likely edit locations, generate many small candidate patches, generate possible reproduction tests, then use regression and reproduction evidence to select a patch.

The study establishes a strong 2024 baseline for issue-sized Python bug fixing. It does not show that fixed pipelines remain sufficient for long, evolving, or ambiguous engineering projects.

## Exact claims and evidence

- **SWE-bench Lite result (direct result):** GPT-4o Agentless resolves `96 / 300` issues (`32.0%`) at reported average cost `$0.70` and `78,166` tokens. It is the best open-source result listed in Table 1, not the best result overall; several closed systems score higher.
- **SWE-bench Verified result (reported evaluation):** Agentless resolves `194 / 500` (`38.8%`), second among the listed open-source approaches and best among listed GPT-4o configurations. Table 6.
- **Localization is a major bottleneck (direct result):** combined prompt and embedding file localization retains a ground-truth file for `81.67%` of issues. Skeleton-based element localization is cheaper and retains more ground-truth locations than full-file input (`58.33%` versus `53.67%`). Table 2.
- **Sampling helps, then plateaus (direct result):** four location samples times ten patches reaches `96` fixes versus `88` for 40 patches from one greedy location and `85` for merged locations. Performance plateaus around 40 candidate patches. Table 3 and Figure 6.
- **Validation improves selection (direct result):** majority vote alone yields `77` fixes; regression filtering yields `81`; generated reproduction filtering yields `96`, adding about `$0.25` average cost. Table 4.
- **Generated tests are unreliable (direct result):** 213/300 generated tests reproduce a failure on the base repository, but only 94 also recognize the ground-truth patch as fixed. Section 5.1.3.
- **Benchmark defects are material (manual dataset analysis):** 10.0% of Lite issues lack enough information, 4.3% contain the exact patch, and 5.0% contain misleading solution guidance. The filtered Lite-S subset contains 249 issues. Section 6.1.

## Method

- Hierarchical localization first ranks suspicious files using repository structure plus embedding retrieval, then ranks class/function skeletons, then selects precise edit locations from full local snippets.
- Repair uses Search/Replace diffs over bounded snippets. It samples four edit-location sets and ten candidate patches per set by default.
- The system generates up to 40 reproduction tests, runs them on the original repository, normalizes them, and chooses the most common test that reports reproduction.
- It identifies passing base tests, asks an LLM which may no longer be valid, and treats the remainder as regression tests.
- Candidate patches are first minimized for regression failures, then filtered by the generated reproduction test. If none passes that test, selection falls back to regression evidence. Normalized-patch majority voting chooses the submission.
- The paper uses GPT-4o for Agentless and compares mostly against reported leaderboard results from systems using differing models, tools, and disclosure levels. Cost is computed from model calls, excluding embedding cost.

## Ablations and failure evidence

- Prompt-only and embedding-only localization are worse than their combination. Full-file context is costlier and less accurate than skeletons.
- Direct file-to-edit localization is worse and more expensive than hierarchical localization.
- More patch samples stop improving the selected-patch score even though the union contains up to 126 solvable issues, showing patch ranking is a bottleneck.
- Only 94 of 213 base-reproducing tests validate the ground-truth fix. Generated tests are helpful aggregate filters, not trusted oracles.
- Closed agent tools do better when issue descriptions provide no location clue, suggesting interactive search can help on harder localization cases.

## Limitations and transfer risks

- Most comparisons are not controlled for model, tool surface, budget, or implementation; the paper primarily establishes a competitive baseline, not a causal advantage over agents.
- SWE-bench Lite is Python bug fixing, not multi-step repository evolution. Contamination is possible with a closed model.
- Ground-truth edit-location overlap is only an approximate localization metric because different patches may be correct.
- Generated tests may encode issue ambiguity or false behavior. Regression tests also depend on an LLM deciding which existing tests should be excluded.
- Agentic Engineering's M03 only evaluates prepared candidates. It is “agentless-style” in being deterministic and single-pass, but it does not reproduce Agentless localization, patch sampling, or test generation.

## Project transfer decision

- **Adopt:** every complex workflow must be compared with the cheapest credible fixed pipeline or canonical single-agent baseline.
- **Adapt:** bounded repository maps and targeted code context are useful inputs, but should be tested per task rather than generated universally.
- **Adapt:** sample-and-filter repair can be an optional issue-fixing strategy when reliable regression evidence exists.
- **Reject:** treating generated reproduction tests as authoritative without independent contract review or counterexample evidence.
- **Defer:** a full Agentless reproduction; current research priority is long-horizon evolution where its task assumptions may not transfer.

## Open questions

- How does the fixed pipeline compare with current agents under the same modern model, task set, and total budget?
- Can independently reviewed properties improve reproduction-test validity?
- Where is the task-size boundary beyond which fixed localization/repair/validation is insufficient?
