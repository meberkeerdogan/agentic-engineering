# Harder Test Design for Agentic Engineering

## Goal

Create tests that are difficult enough to reveal workflow differences but small enough to run repeatedly. This is an evaluation project, not a new agent feature.

## Test ladder

### Level 1: Multi-target upgrade

- Existing repository with roughly 5-20 source files and at least 500 source lines.
- One clear upgrade containing 3-5 meaningful targets across at least 4 files.
- Separate hidden tests for each target plus protected existing tests.
- Full completion requires every target and protected test to pass.
- Partial score reports the unweighted fraction of targets passed. A second strict score becomes zero when protected behavior regresses.

Purpose: replace the present 8-12-line fixtures as the normal workflow comparison.

### Level 2: Continuous evolution

- One persistent repository receives 4-6 milestones.
- Include at least one dependency branch and one later integration milestone.
- Every milestone has required-change tests and protected tests from earlier milestones.
- Run each milestone twice: once from the correct canonical starting point and once continuously on the agent's own accumulated repository.
- Snapshot and independently evaluate every submission.

Purpose: measure how much correctness is lost through error accumulation. The difference between isolated and continuous results is the main signal.

### Level 3: Release-scale external check

- Use a small selected slice from SWE-EVO, RoadmapBench, or SWE-Milestone only after Levels 1 and 2 work.
- Freeze the paper artifact, environment, task IDs, model, scaffold, and budget.
- Report deviations from the paper and do not call a small slice a full reproduction.

Purpose: test whether local findings transfer beyond our own fixtures.

NL2Repo-style empty-workspace generation is deferred. It can later serve as a packaging smoke test, but it is not required to validate the existing-repository v0.1 workflow.

## Metrics

Primary measures:

- full independently verified completion;
- protected regressions;
- false completion;
- continuous-versus-isolated score gap.

Partial and diagnostic measures:

- targets passed;
- required tests fixed;
- previously passing tests broken;
- inherited failures and later recoveries;
- premature completion or unfinished run;
- repeated edits, meaningful test runs, steps, cost, time, and human intervention.

Activity metrics are diagnostic only. More turns, reads, edits, or tests do not count as progress by themselves.

## Task-quality gate

Before any paid comparison, every task must pass these checks:

1. The initial repository builds and its protected tests pass.
2. At least one required target test fails initially.
3. A known oracle solution passes every target and protected test.
4. Every hidden assertion maps to a stated requirement.
5. Instructions do not reveal hidden test names, oracle code, or future-version history.
6. Tests are deterministic in a clean local environment.
7. Two reviewers classify observed failures as task defects or real agent failures; task defects are repaired before the evaluation set is frozen.
8. Pilot calibration and final evaluation use different tasks.

## Comparison design

- Start with the simple canonical-rereading workflow as control.
- Hold model, tools, repository, task text, evaluator, context/step limits, and budget equal.
- Use at least three repeated runs per task and arm, while clearly stating that the CLI seed is a run label rather than control of model randomness.
- Preserve paired per-task results, not only averages.
- Use pilot tasks to select a useful difficulty band. Freeze held-out evaluation tasks before the final comparison.
- Prefer tasks where the pilot control completes roughly 20-80% of targets. Exclude universal-pass ceilings and universal-fail floors from efficacy claims, but preserve them as calibration evidence.

## Promotion rule

Do not promote a workflow from activity or one favorable run. A treatment must improve full completion, strict partial progress, or continuous reliability on the frozen tasks without increasing protected regressions or false completion. Report cost and time even when quality improves.

## Bounded implementation order

1. Extend evidence reports with grouped target results and strict partial scoring.
2. Build one Level 1 fixture and validate it entirely offline.
3. Build one Level 2 milestone chain and validate isolated and continuous oracle paths.
4. Add enough held-out tasks to avoid one-fixture conclusions.
5. Run one low-cost live safety sentinel.
6. Only if the sentinel produces useful variation, predeclare and run a repeated efficacy comparison.

This order has a stopping rule: if offline tasks are invalid, or the sentinel produces another complete ceiling or complete floor, repair the task design before spending on a full matrix.

## Implementation status and release decision

As of 2026-08-20, steps 1-3 are complete and pass the full offline suite. Level 1 starts at `0/5` targets with no protected regression and reaches `5/5` with its oracle. Level 2 has five milestones whose isolated and continuous oracle paths match; intentionally omitting the first milestone creates a later protected regression.

Steps 4-6 remain required before claiming that a workflow improves long-task agent performance. They do not block `v0.1` packaging because the release is an experimental workflow toolkit, not a proven efficacy claim. Product work now returns to the finite finish line in [ROADMAP.md](../../../ROADMAP.md).
