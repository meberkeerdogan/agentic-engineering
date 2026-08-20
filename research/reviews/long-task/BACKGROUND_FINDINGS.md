# Long-task evaluation: background findings

## Question

What do primary benchmark papers teach us about building long and complex coding tests that are hard enough to reveal workflow value, but still fair, measurable, and affordable?

This review covers four local papers:

- [SWE-EVO](../../papers/2512.18470-swe-evo.pdf)
- [RoadmapBench](../../papers/2605.15846-roadmapbench.pdf)
- [SWE-Milestone](../../papers/2603.13428-swe-milestone.pdf)
- [NL2Repo-Bench](../../papers/2512.12730-nl2repo-bench.pdf)

The paper summaries below report what the papers say. The final section is our inference for Agentic Engineering. A reported association, such as more testing appearing in better runs, is not treated as proof that the behavior caused the improvement.

## Evidence at a glance

| Benchmark | What the agent must do | Scale | Main progress measure | Main result | Important evidence limit |
| --- | --- | --- | --- | --- | --- |
| SWE-EVO | Move an existing Python project from one release to the next from release notes and linked issue text | 48 tasks, 7 repositories | Full resolution plus regression-gated Fix Rate | Table 2 ranges from 2.08% to 39.58% resolved, depending on model and scaffold | One task changes the result by 2.08 points; 26 of 48 tasks come from one repository; no repeated trials are reported |
| RoadmapBench | Implement several targets from one real version upgrade | 115 tasks, 17 repositories, 5 languages, median 5 targets | Full resolution plus weighted target completion | Best reported resolution is 39.1%; best Completion Score is 0.692 | One trial per model; target weights involve judgment; task selection and repair use model rollouts |
| SWE-Milestone | Complete a stream of dependent milestones in one persistent codebase | 98 milestones, 7 release ranges, 5 languages | Feature recall, regression precision, their harmonic mean, and strict resolution | Best continuous score is 38.03%; best strict resolution is 13.37%; isolated milestones exceed 80% | No repeated agent trials are reported; public repositories may be in training data; only 7 evolution ranges |
| NL2Repo-Bench | Build a complete Python repository from an empty folder and one long specification | 104 tasks, 9 categories | Mean upstream-test pass rate and fully passed repository count | Best mean score is 40.2%; the maximum full-repository count is 5 of 104 | One run per configuration is reported; network access is not described as blocked; no dedicated limitations section or contamination study |

## 1. SWE-EVO

### Paper results

**Task construction.** SWE-EVO starts from SWE-bench and SWE-gym environments, keeps candidates whose base commit is a tagged release, and asks an agent to reproduce the behavior of the next tagged release. Candidates must have at least one test that fails before the human patch and passes afterward. Installation and runtime failures are removed. Human review then checks the release note, linked pull requests or issues, gold patch, and tests, leaving 48 release-sized tasks across 7 Python repositories. The average task has a 2,390-word specification, a gold patch touching 20.9 files and 610.5 lines, 81.4 required-change tests, and 874 total tests. [SWE-EVO, Sections 3.1-3.3 and Table 1](../../papers/2512.18470-swe-evo.pdf)

**Agent input and controls.** The agent receives the source release and a release-note-centered specification. The default condition also includes the original text of linked pull requests and issues. Internet access is blocked so the agent cannot fetch target-version code during the run. The study evaluates OpenHands and SWE-agent with a limit of 100 iterations or model calls and medium reasoning effort. Eighteen models are listed, but repeated runs are not reported. The prose says the models come from five providers, while its own model table groups six provider families. [SWE-EVO, Sections 4.1-4.2 and Appendix A and N](../../papers/2512.18470-swe-evo.pdf)

**Metrics.** A task is resolved only when every required-change test and every regression test passes. Fix Rate gives partial credit for the fraction of required-change tests fixed, but sets the task score to zero if any protected regression test fails. Patch Apply Rate separately reports whether the patch can be applied. The authors correctly warn that Fix Rate does not measure maintainability, code quality, or patch simplicity. [SWE-EVO, Section 3.2](../../papers/2512.18470-swe-evo.pdf)

**Results and failure evidence.** Table 2 reports resolved rates from 2.08% to 39.58%, with large scaffold effects for some models. Partial Fix Rates are usually higher than full resolution, showing incomplete progress. The paper's text and abstract call GPT-5.4 at 25% the best result, but Table 2 reports SWE-agent results of 37.50% for GLM-5 and 39.58% for GLM-4.7. This internal mismatch means the headline should not be repeated without the table caveat. The trajectory analysis labels strong-model failures mainly as requirement misunderstanding and weaker-model failures more often as bad implementation, tool use, or syntax problems. Those labels come from an LLM judge and were not human-validated. Tasks unresolved by every evaluated combination average 14.84 linked pull requests, compared with 1.67 for the easiest group. [SWE-EVO, Sections 4.2-4.3, Tables 2 and 6, and Figure 6](../../papers/2512.18470-swe-evo.pdf)

**Limits and leakage risk.** Forty-eight tasks provide limited statistical power: one solved task moves the score by 2.08 percentage points. The paper reports wide Wilson confidence intervals and says close rankings should not be overinterpreted. The dataset is Python-only, 54.2% of tasks come from `dvc`, and task text covers only release-note-driven work. Internet blocking prevents direct future-code lookup, but the tasks come from mature public repositories already used in earlier benchmark ecosystems. The paper does not test whether models memorized these repositories or releases. [SWE-EVO, Section 6 and Appendix H](../../papers/2512.18470-swe-evo.pdf)

## 2. RoadmapBench

### Paper results

**Task construction.** RoadmapBench selects repositories with at least 1,000 stars, at least five releases, activity through 2025, and detailed release documentation. Experts choose consecutive version pairs with at least 500 changed lines and deterministic user-visible behavior. Each task places the agent at the older release and gives it a roadmap describing several target behaviors without implementation steps. The final set contains 115 tasks from 17 repositories and 5 languages. A task has 3 to 12 targets, with a median of 5, and a median human patch of about 3,714 changed lines across 51 files. [RoadmapBench, Sections 3.1-3.3 and Appendix G.1](../../papers/2605.15846-roadmapbench.pdf)

**Quality control.** Tests are adapted from upstream tests and assigned to individual targets. Review checks that every tested behavior appears in the instruction and that tests avoid hidden assumptions or internal implementation details. Agents from three capability levels then attempt the task. Experts classify failures as task defects or model failures, repair task defects, and rerun validation. Forty-five of 115 tasks needed at least one repair cycle, averaging 3.1 cycles. On Terminus, quality control raised Claude Opus 4.6 resolution from 19.1% to 30.4%, showing that benchmark defects can materially understate agent ability. Agreement on task-defect versus model-failure attribution was strong on 40 double-reviewed trajectories (Cohen's kappa 0.83). [RoadmapBench, Section 3.3 and Appendix G.2-G.3](../../papers/2605.15846-roadmapbench.pdf)

**Agent setup and metrics.** Thirteen models run through OpenHands, and a subset also runs through Terminus 2. Each task has a two-hour limit and extended reasoning. The agent cannot see target code, tests, or the gold patch; future branches and upstream access are blocked. Full resolution requires every target to pass. Completion Score is the weighted fraction of targets passed. The paper also reports turns and output tokens. Every model has one trial, so small differences may reflect run variation. [RoadmapBench, Section 4.1 and Table 2](../../papers/2605.15846-roadmapbench.pdf)

**Results and failure evidence.** Under OpenHands, Claude Opus 4.7 resolves 39.1% of tasks with a 0.692 Completion Score. The weakest result is 5.2% resolved with a 0.177 Completion Score. This gap between complete and partial scores shows that agents often finish several targets but fail at integration or later targets. Resolution falls as file count, changed lines, and target count grow. Component creation has a 36% average target pass rate, compared with 64% for bug fixes. Most models gain little after about 200 steps; more calls help only when the model turns them into focused edits and verification. Of 3,603 failed subtasks classified by an agentic judge, implementation errors are 39%, build errors 28%, missing work 23%, interface mismatches 6%, and agent failures 4%. A 50-item human check reports 88% category agreement. [RoadmapBench, Sections 4.2 and 5.1-5.6, plus Appendix H](../../papers/2605.15846-roadmapbench.pdf)

**Limits and leakage risk.** Results depend on the agent scaffold, and tests do not measure maintainability or idiomatic code. The benchmark covers more languages than SWE-EVO but only 17 public repositories. Repository and version names are hidden, future git history is pruned, and upstream access is blocked. These controls reduce direct lookup. They do not show that model training data excluded the public target releases. Task inclusion also requires different model tiers to receive distinguishable scores, and model rollouts drive task repair. That improves usability but can make the benchmark especially fitted to the tested model population. The paper does not describe how target-complexity weights are independently calibrated. Its repository table uses Python, TypeScript, C++, Go, and Rust, while one appendix checklist names Java instead of C++, another small internal documentation error. [RoadmapBench, Appendix A, E, and G](../../papers/2605.15846-roadmapbench.pdf)

## 3. SWE-Milestone

### Paper results

**Task construction.** SWE-Milestone uses DeepCommit to turn commits between releases into functionally coherent milestones connected by dependencies. Static analysis builds commit, symbol, and file relationships. LLM agents identify seed commits, group related commits, infer dependencies, and split oversized groups. A separate process reconstructs executable milestone states, builds Docker environments, repairs dependency errors, and filters flaky tests with three runs. The benchmark then keeps core functional milestones with executable required-change tests and manageable context size. Experts review specifications for solvability and implementation leakage. The result is 98 milestones in 7 dependency graphs across 5 languages, with 109 dependency edges. A milestone changes 27.4 files on average and has 17.1 required-change tests plus 6,218 regression tests on average. [SWE-Milestone, Sections 3-4 and Figure 4](../../papers/2603.13428-swe-milestone.pdf)

**The key comparison.** The same milestone is tested in two ways. In the independent condition, the agent starts from the correct human snapshot for that milestone. In the continuous condition, it keeps its own earlier changes and receives later milestones only when their dependencies are complete. Each submitted state is copied into an isolated container for scoring. This comparison separates local task difficulty from damage that accumulates across a project. [SWE-Milestone, Sections 4.1 and 5.1](../../papers/2603.13428-swe-milestone.pdf)

**Metrics and setup.** Recall measures how many required behaviors the agent implemented. Precision measures whether test-status changes are improvements rather than regressions. Their harmonic mean is the main Score, so ignoring new work and breaking old work are both penalized. Strict Resolve Rate requires all required-change and regression tests to pass. The study reports 12 models across Claude Code, Codex CLI, Gemini CLI, and OpenHands, forming 15 model-agent configurations. It reports one aggregate trajectory per configuration and does not describe repeated seeds. A full frontier-model evaluation is said to cost about $500. [SWE-Milestone, Section 5.1 and Table 2](../../papers/2603.13428-swe-milestone.pdf)

**Results and failure evidence.** Isolated milestone scores exceed 80%, while the best continuous Score is 38.03% and the best strict Resolve Rate is 13.37%. Later milestones and deeper dependency layers score worse. Feature recall keeps rising, but regression precision reaches a ceiling. Error-chain analysis shows early mistakes being inherited by later milestones; logic errors dominate the reviewed error chains. Agent behavior is also revealing: better runs explore more, verification usually increases as the project grows, and high repeated editing with little testing performs worst. These are associations from observed trajectories, not controlled tests of exploration or verification policies. [SWE-Milestone, Sections 5.2-5.6](../../papers/2603.13428-swe-milestone.pdf)

**Limits and leakage risk.** The benchmark depends on strong existing test suites, filters out loosely connected and documentation-only work, and therefore favors dependency-rich, testable evolution. It covers only seven release ranges and limits source changes to roughly 30,000 lines. Human guidance remains part of environment repair and specification review. The paper directly acknowledges that the high-impact public repositories may be present in training data and that memorization cannot be ruled out. It proposes new commits or private repositories as stronger contamination controls. DeepCommit also recovers structural dependencies better than human intent: its case study finds that it can split one human development theme into several code-topology phases and omit process conventions. [SWE-Milestone, Limitations and Section 5.7](../../papers/2603.13428-swe-milestone.pdf)

## 4. NL2Repo-Bench

### Paper results

**Task construction.** NL2Repo-Bench starts from Python libraries with 300 to 120,000 lines, at least 10 stars, recent activity, and a passing pytest suite. Annotators reverse-engineer each project into a single specification containing the project purpose, dependencies and expected folder structure, an API guide, and detailed implementation nodes. An AST scanner checks that classes, functions, signatures, and relevant semantics are documented. Human experts review the result, and strong-agent dry runs are used to find ambiguous specifications or broken environments. The final set has 104 tasks in 9 categories. Specifications average about 18,800 tokens; tasks are grouped by original repository size into 26 easy, 46 medium, and 32 hard tasks. [NL2Repo-Bench, Sections 3.1-3.2](../../papers/2512.12730-nl2repo-bench.pdf)

**Agent setup and metrics.** An agent starts in an empty workspace with only the specification and must create an installable repository. The original upstream pytest suite is hidden until evaluation. Most models run in OpenHands; Gemini 3 Pro runs in Cursor because of an OpenHands loop problem, and Claude Sonnet 4.5 is also compared across OpenHands, Cursor, and Claude Code. The main runs have no interaction-round limit. The score is the mean fraction of upstream tests passed. Pass@1 is reported as the number of repositories whose entire suite passes in the single run. [NL2Repo-Bench, Sections 4.1-4.2](../../papers/2512.12730-nl2repo-bench.pdf)

**Results and failure evidence.** The best mean score is 40.2%, from Claude Sonnet 4.5 in Claude Code, and that configuration fully passes 3 of 104 repositories. The largest full-pass count is 5 of 104, from Claude Sonnet 4. Average score drops from 51.8% on easy tasks to 25.1% on hard tasks for the top-scoring configuration. More turns do not guarantee better results. Claude combines persistence with a repeated edit-test loop, while some models spend many steps navigating or edit repeatedly without testing. GPT-5 averages 78.4 turns and has an 84.5% non-finish rate, mainly because it waits for human input; Qwen3-Thinking finishes in fewer than 100 turns on 49% of tasks. Raising Claude's limit from 50 to 200 rounds helps, but more than 200 gives little additional gain. Revealing all tests raises Claude's mean score from 40.2% to 59.4% and full passes from 3 to 18, but still leaves substantial failure. The abstract says the best result is below 40%, and the conclusion gives 39.6%, so Table 3's 40.2% should be treated as the current detailed result. [NL2Repo-Bench, Sections 4.2-4.4 and Tables 3, 6, and 8](../../papers/2512.12730-nl2repo-bench.pdf)

**Limits and leakage risk.** The benchmark covers only Python libraries and scores functional tests, not maintainability or design quality. Difficulty is based only on original lines of code, which is a rough proxy for real difficulty. The paper does not provide a dedicated limitations section, repeated-seed results, confidence intervals, or an annotation-agreement study. More importantly, it says agents may use any available tool, and its OpenHands tool list includes browser and URL-fetch tools. It does not report blocking internet access or hiding repository identity. Because tasks come from public repositories and specifications expose structure, APIs, dependencies, and examples, direct source lookup or training-data memorization is not ruled out. This is an inference from the reported setup, not a leakage event demonstrated by the paper. [NL2Repo-Bench, Sections 4.1 and Appendix B](../../papers/2512.12730-nl2repo-bench.pdf)

## Cross-paper findings

These conclusions are directly supported by more than one paper:

1. **A long task needs meaningful intermediate results.** Full pass or fail hides whether the agent completed most targets, implemented new behavior while causing regressions, or made no progress. SWE-EVO uses test-level Fix Rate, RoadmapBench uses target completion, SWE-Milestone separates feature progress from regressions, and NL2Repo-Bench uses test pass rate.
2. **Long-task difficulty is not just token length.** More targets, files, lines, dependencies, and later project position all reduce performance. NL2Repo-Bench also shows that adding more steps stops helping once the agent can no longer turn them into coherent work.
3. **Regression accumulation is the clearest long-horizon failure.** SWE-EVO penalizes regressions, RoadmapBench finds integration and build failures, and SWE-Milestone directly shows early damage spreading into later milestones.
4. **Benchmark quality control changes the measured result.** RoadmapBench's repair cycle moved one model by 11.2 resolution points. All four papers use human review or strong-agent dry runs to find broken tests, ambiguous requirements, or environment failures.
5. **A single trajectory is weak evidence for close comparisons.** RoadmapBench explicitly uses one trial per model; the other three report no repeated agent seeds. Their broad difficulty conclusions are useful, but small workflow differences would need paired repeated runs.
6. **Public-repository leakage remains unresolved.** Blocking internet and pruning future git history prevent direct copying during a run. They do not prove that model training excluded an older public release. Only SWE-Milestone states this limitation directly.

## Inference for Agentic Engineering

The following is our design judgment, not a result reported by any one paper.

### What kind of test we need

For the next workflow comparison, use **existing-project evolution**, not full repository generation. It is closer to the product we built and is cheaper to verify than starting from an empty folder.

Each test should contain:

- one source repository snapshot with future history removed;
- 3 to 6 clearly separated targets;
- at least one dependency where a later target relies on an earlier design choice;
- changes across several files and modules;
- hidden required-change tests for each target;
- protected regression tests that run after every stage;
- one gold implementation that proves the task and tests are valid;
- an isolated evaluator that the working agent cannot edit.

The simple control workflow should solve roughly 20% to 70% of the tasks. Above that range, a ceiling hides improvement. Far below it, both arms may fail for reasons unrelated to the workflow. Difficulty should be adjusted by target count, dependency depth, affected files, and integration boundaries rather than by making instructions vague.

### What to measure

Use three levels of results:

1. **Product outcome:** full task completion with no regression.
2. **Partial progress:** targets passed, required behaviors implemented, and protected behavior preserved.
3. **Process evidence:** repeated edits, test runs, repeated failures, premature stopping, budget use, time, and whether an earlier defect blocks a later target.

Completion remains the primary result. Partial and process measures explain why it changed; they must not be used to declare success when the product outcome gets worse.

### Fair comparison

Compare the default Agentic Engineering workflow with a small, credible control using the same model, task snapshot, tools, hidden evaluator, time, step, context, and credit limits. Run at least three paired seeds per task and keep every run, including failures. Predeclare the primary metric and promotion rule before authenticated calls.

Start with a small pilot of 4 to 6 validated tasks. Promote the benchmark only if the control is below the ceiling, the evaluator is stable, and at least two different failure types appear. A larger paid campaign should wait until that pilot passes.

### Leakage controls

- Use repositories or changes created after the model's likely training cutoff when possible.
- Prefer private or locally generated variants for the strongest contamination control.
- Remove future commits, tags, branches, and package/version names from the task workspace.
- Block network access during evaluation.
- Do not reveal hidden tests or the gold patch.
- Record source dates and hashes so later benchmark revisions remain auditable.

### What not to copy

- Do not use only a binary final score.
- Do not treat raw lines changed as the whole definition of difficulty.
- Do not allow unlimited steps; several papers show that extra steps often saturate.
- Do not select tasks only because the treatment workflow performs better on them.
- Do not add a complex milestone generator to the product now. A small human-designed dependency graph is enough to test the current workflow.
- Do not claim that exploration, planning, or frequent testing caused higher scores until each policy is isolated in a controlled comparison.

## Review decision

These papers justify replacing the earlier ceiling tasks with a bounded multi-target evolution pilot. They do not justify another workflow feature yet. The next engineering work should be benchmark design and evaluator validation, followed by one low-cost control pilot. The result should decide whether a treatment experiment is worth running; research should not delay the finite `v0.1` product path unless it reveals a correctness or safety problem.
