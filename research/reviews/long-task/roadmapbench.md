# Paper Dossier: RoadmapBench

## Identity and review scope

- Local PDF: [`2605.15846-roadmapbench.pdf`](../../papers/2605.15846-roadmapbench.pdf)
- Manifest SHA-256: `6623545995103c66ecea898a8190af10115058c4469b53e49d2730a1dc2c98ba`
- Version or date: arXiv v2, 2026-05-19; 30 pages
- Workflow section: long-task evaluation
- Review question: how should multi-target version upgrades be specified, scored, and checked for benchmark defects?
- Relevant evidence: Sections 3-6; Tables 2-6; Figures 2-9; Appendices G-H

## Plain-English contribution

RoadmapBench turns real version upgrades into roadmaps with several named targets. It checks each target separately, so an agent can receive partial credit instead of one uninformative failure. Its construction process also tests the tests: many draft tasks had unclear requirements or unfair checks and needed repair before evaluation.

## Exact claims and evidence

- **Scale (direct):** 115 tasks from 17 repositories and five languages. A task has 3-12 targets, with a median of five; the target-version patch has a median of roughly 3,700 changed lines and 51 files. Section 3.2 and Figure 3.
- **Main result (direct, one trial):** with OpenHands, Claude Opus 4.7 resolves `39.1%` with a `0.692` Completion Score; GPT-5.4 resolves `29.6%` with `0.497`. Table 2 explicitly says one trial per model.
- **Partial-progress gap (direct):** Claude Opus 4.6 resolves `32.2%` but completes a weighted `62.7%` of targets. Seed 2.0 Pro resolves `5.2%` but completes `17.7%`. Table 2.
- **Difficulty pattern (direct):** more files, more changed lines, and more targets all reduce success. The strongest separation appears in the middle ranges; tasks above 10,000 changed lines are close to a floor even for strong models. Figure 7.
- **Quality-control effect (direct):** 45 of 115 tasks needed at least one repair round, averaging 3.1 rounds. For Claude Opus 4.6 under Terminus, post-repair resolved rate rose from `19.1%` to `30.4%`. Table 4. Benchmark defects can therefore overwhelm model comparisons if task quality is not checked.

## Method

- Repositories require active releases, at least 1,000 stars, and useful release documentation. Experts select source-to-target version pairs.
- Future branches and tags are removed. Upstream access, target code, tests, and oracle patches are unavailable to the agent.
- A roadmap describes externally visible targets without exposing implementation steps. Adapted upstream tests are grouped by target and weighted by implementation complexity.
- Static reviews check instruction completeness, implementation leakage, public API clarity, hidden-test leakage, deterministic tests, and instruction-test alignment.
- Three capability tiers attempt each draft task. Experts distinguish benchmark defects from model failures and repair the task until the oracle passes, no known task-side errors remain, and scores discriminate among models.
- Each model gets a two-hour task budget. Full resolution requires every target; Completion Score is the weighted fraction of targets passed.

## Ablations and failure evidence

- Most models perform better under OpenHands than Terminus, but two models reverse the direction. Scaffold choice can change conclusions.
- More steps help only when the model converts them into useful work. Most models saturate by roughly 200 steps.
- Component creation is harder than bug fixing. Strong-agent failures concentrate in subtle logic, misunderstanding, and wiring; weaker-agent failures more often fail to build or omit work.
- Failure categories are assigned by an LLM classifier. A 50-case manual sample reports 88% category agreement, but subtype accuracy is lower.

## Limitations and transfer risks

- Main model results are single trials, so run-to-run uncertainty is not measured.
- Task construction uses frontier-agent rollouts and expert repair. This improves fairness but can tune tasks toward the agents used during construction.
- Target weights involve judgment and can change the Completion Score without changing behavior.
- Large public repositories and release histories may appear in model training data.
- A full RoadmapBench run is too expensive for routine Agentic Engineering development; its quality-control process is more immediately reusable than its scale.

## Project transfer decision

- **Adopt:** name 3-7 meaningful targets and score them separately, with full completion remaining the main release criterion.
- **Adopt:** require an oracle solution and a formal task-quality checklist before a task enters a paid comparison.
- **Adapt:** calibrate medium-difficulty tasks on separate pilot runs, then freeze held-out tasks to avoid tuning evaluation to one agent.
- **Adopt:** record steps, tool use, cost, and time, but never treat raw activity as progress.
- **Defer:** target weights based on human effort until unweighted and weighted reports can be compared.

## Open questions

- How stable are the one-trial rankings under repeated seeds?
- How were target weights calibrated across languages and repositories?
- How much rollout-based repair improves fairness versus overfitting tasks to the construction agents?
