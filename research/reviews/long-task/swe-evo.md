# Paper Dossier: SWE-EVO

## Identity and review scope

- Local PDF: [`2512.18470-swe-evo.pdf`](../../papers/2512.18470-swe-evo.pdf)
- Manifest SHA-256: `cfa2ca71f3bd14ed93021a00d39767be80d7e2843c47f7d7ca11cf50dc9767d8`
- Version or date: arXiv v6, 2026-05-22; 30 pages
- Workflow section: long-task evaluation
- Review question: how should release-sized software evolution be turned into executable, non-ceiling tests?
- Relevant evidence: Sections 3-6; Tables 1-2 and 4-8; Figures 4-6; Appendices H-J and N

## Plain-English contribution

SWE-EVO asks an agent to move a real Python library from one release to the next. The agent receives the old code and release notes, sometimes with linked issue text, and must make many coordinated changes without breaking existing behavior. It is a much harder test than fixing one isolated bug.

## Exact claims and evidence

- **Scale (direct):** 48 manually checked release transitions from seven Python libraries. A task averages 2,390 specification words, 610 edited lines, 21 edited files, 51 edited functions, 81 required-change tests, and 874 total tests. Table 1.
- **Matched difficulty gap (direct):** GPT-5.2 with SWE-agent scores `22.92%` on SWE-EVO, compared with the paper's cited `72.80%` SWE-bench Verified result. Table 2.
- **Partial progress (direct):** GPT-5.4 averages `25.00%` resolved and about `33.96%` Fix Rate across the two scaffolds. Other models also have Fix Rates above their resolved rates, showing incomplete but real progress. Table 6.
- **Complexity pattern (direct):** tasks unresolved by every model-scaffold pair average `14.84` linked pull requests; the easiest group averages `1.67`. Figure 6.
- **Important paper inconsistency:** the abstract, conclusion, and Table 2 discussion call GPT-5.4 at `25%` the best result, but Table 2 visually reports `39.58%` for GLM-4.7 with SWE-agent and `37.50%` for GLM-5. The stored v6 paper therefore does not support an unqualified “best result is 25%” claim.

## Method

- Candidate tasks come from SWE-bench and SWE-gym repositories with working environments, then require a base commit that is exactly a release tag.
- The requirement is the release-note change to the next version. The default setting includes text from linked pull requests or issues but withholds an oracle decomposition.
- A task stays only when at least one target test fails before the gold patch and passes afterward, the environment is stable, and human reviewers confirm alignment among requirements, changes, and tests.
- Agents receive the source repository with internet access blocked. OpenHands and SWE-agent each receive a maximum of 100 iterations or model calls.
- Full resolution requires every required-change and protected regression test to pass.
- Fix Rate gives partial credit for required tests fixed, but becomes zero if any protected test regresses.

## Ablations and failure evidence

- Release-note-only instructions perform somewhat worse than instructions augmented with issue and pull-request text, so requirement detail matters.
- The paper's automatic failure labels suggest strong models more often misunderstand broad instructions; weaker models show more incorrect implementations, tool errors, syntax errors, loops, and early exits. These labels come from an LLM judge and lack human agreement validation.
- Results change materially across OpenHands and SWE-agent for some models. The benchmark measures model-plus-scaffold behavior, not the model alone.
- Only 48 tasks means one solved task changes the score by 2.08 percentage points. The paper reports wide Wilson intervals and warns against close leaderboard comparisons.

## Limitations and transfer risks

- Twenty-six of 48 tasks come from `dvc`; all projects are Python libraries.
- Equal test weighting can misrepresent feature importance. Fix Rate does not measure maintainability, design quality, or patch simplicity.
- The release-sized task hides intermediate structure. It diagnoses final evolution ability but does not reveal exactly which milestone failed unless tests are grouped carefully.
- Agentic Engineering's present “multi-step” fixture contains two tiny source files and six target tests. It is a safety fixture, not a SWE-EVO-scale task.

## Project transfer decision

- **Adopt:** separate new-behavior tests from protected regression tests and give partial credit only while regressions remain controlled.
- **Adapt:** use smaller multi-target release tasks first, with named targets and grouped tests, instead of immediately copying 48 expensive release transitions.
- **Adopt:** block future-version code and keep task instructions independent from hidden tests.
- **Reject:** using one full-task pass/fail number as the only long-task measure.
- **Defer:** a full SWE-EVO reproduction until the local medium-scale test ladder proves affordable and informative.

## Open questions

- Which v6 result is intended as the headline: GPT-5.4 at 25% or the larger GLM SWE-agent values in Table 2?
- How stable are model rankings across repeated runs?
- Can target-weighted tests preserve strict regression handling without allowing many easy tests to dominate?
