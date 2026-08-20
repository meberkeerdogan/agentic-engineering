# Long-Horizon Agent Reliability: Critical Research Review

**Review date:** 2026-08-14

**Scope:** Nine papers on long-horizon software engineering, planning, context, evaluation, testing, orchestration, and monitoring

**Input:** The workflow proposal preserved in the original project discussion

## Executive Conclusion

The supplied workflow has a strong evidence-backed core, but some proposed mechanisms were stated more confidently than the papers justify.

The most defensible reusable foundation is:

1. define executable success criteria before implementation;
2. keep authoritative project state outside the executor's conversation;
3. give a fresh, bounded executor one verified unit of work;
4. have an independent, preferably read-only evaluator inspect the real artifact or environment;
5. update persistent state only from evidence;
6. preserve the best-known state and reject unexplained regressions;
7. monitor trajectories for known failure patterns and replan when evidence warrants it.

This should first be implemented as an observable manual protocol and experiment harness. A universal milestone DAG, fixed anti-loop thresholds, or a large autonomous orchestrator should not be the first deliverable. Those are promising interventions that must earn adoption through local A/B tests.

## What the Evidence Supports

| Proposed claim | Evidence judgment | Confidence | Project implication |
| --- | --- | --- | --- |
| Current agents degrade on long, repository-wide work | Repeated across SWE-EVO, RoadmapBench, and SWE-Milestone | High | Treat long-horizon reliability as a measurable systems problem |
| External executable evaluation is more trustworthy than self-reported progress | Directly supported within Progress Mirage's tested setting; consistent with benchmark design | High within bounded scope | Make tests, benchmarks, invariants, or world-state metrics authoritative |
| Fresh execution context plus separate audit can improve long-horizon work | Strong benchmark gains in LongHorizon-Harness | Medium-high | Reproduce manager-executor-auditor locally before standardizing |
| Good plans and reminders can help | Directly supported by Plan-to-Action | Medium-high | Use short task-specific plans and lightweight reminders |
| More repository instructions improve agent success | Not supported by Evaluating AGENTS.md | Low/negative | Keep the top-level agent guide small and specific |
| Milestone DAGs improve arbitrary coding-agent execution | Not established; SWE-Milestone uses DAGs primarily to construct and score a benchmark | Low | Keep DAG scheduling behind an experiment flag |
| Deterministic monitoring can improve issue resolution | Supported by LivePlan under its scaffold and datasets | Medium | Begin in observe-only mode and calibrate locally |
| Fixed universal loop thresholds are research-backed | Not supported | Low | Learn thresholds from trajectory data; do not copy invented constants |
| Agent-generated property tests can find real bugs | Supported, with substantial validity and oracle caveats | Medium | Use property/metamorphic tests as complementary evidence, not an unquestioned oracle |
| Every task requires an out-of-band evaluator | Too broad | Low | Use it when the success signal is outside the transcript/artifact; local deterministic checks suffice for many bounded tasks |

## Findings by Paper

### 1. Long-Horizon Benchmarks

#### SWE-EVO

[SWE-EVO](../papers/2512.18470-swe-evo.pdf) contains 48 release-scale tasks averaging 21 files and 874 tests. Its reported best result is 25%, and GPT-5.2 falls from 72.8% on SWE-bench Verified to 22.92% on SWE-EVO. Its Fix Rate metric exposes partial progress while assigning zero when regressions remain.

What this establishes: isolated issue-resolution results do not transfer cleanly to coordinated software evolution.

Limits: 48 tasks are a small, uneven sample; tasks come from Python libraries and release notes; equal test weighting is imperfect; Fix Rate does not measure maintainability or architectural quality.

#### RoadmapBench

[RoadmapBench](../papers/2605.15846-roadmapbench.pdf) evaluates 115 tasks from 17 repositories across five languages, with a median task size of roughly 3,700 changed lines, 51 files, and five targets. The best reported completion rate is 39.1%.

What this adds: long-horizon weakness persists across a broader language and repository set, and partial-credit scoring is valuable.

Limits: evaluation uses two agent scaffolds; tests do not fully assess maintainability or ecosystem idioms; repository coverage remains finite.

#### SWE-Milestone

[SWE-Milestone](../papers/2603.13428-swe-milestone.pdf) defines 98 human-verified milestones across seven software-evolution DAGs in five languages. Isolated milestone performance exceeds 80%, while the best continuous score is 38.03% and the best full resolution rate is roughly 13%. Recall increases during execution, but precision saturates as errors and regressions accumulate. High-thrash, low-verification trajectories perform worst.

What this establishes: successful isolated changes do not simply compose into reliable continuous evolution; dependency-aware progress and regression measurement are useful evaluation concepts.

What it does **not** establish: adding a milestone DAG manager to any coding workflow causes better execution. That remains a project hypothesis.

Limits include reliance on rich executable tests, a bias toward dependency-rich tasks, possible benchmark contamination, human oversight during construction, and a repository scale around tens of thousands of lines rather than multi-year industrial systems.

### 2. Planning and Context

#### From Plan to Action

[From Plan to Action](../papers/2604.12147-plan-to-action.pdf) analyzes 21,120 SWE-agent trajectories across four models, two benchmarks, and eight plan variants. Good standard plans improve success; subpar plans can perform worse than no explicit plan. Periodic reminders improve compliance and success, but strict compliance is not always beneficial because useful executions sometimes deviate from the proposed order.

Project interpretation: maintain a minimal phase contract and remind the executor of it at natural checkpoints. Avoid a giant universal workflow and permit evidence-backed replanning.

Transfer caveat: plan effects vary by model, task, and scaffold, and repeated runs show nondeterminism.

#### Evaluating AGENTS.md

[Evaluating AGENTS.md](../papers/2602.11988-evaluating-agents-md.pdf) evaluates four agents on SWE-bench and the authors' 138-task CTXBENCH. Repository context files did not significantly improve success and increased steps and cost. Developer-written files were marginally positive and generated files marginally negative, but neither result was statistically significant. Agents did follow the instructions, often doing more testing and exploration.

Project interpretation: use `AGENTS.md` for concise, nonstandard operational constraints that are not discoverable elsewhere. Let it map to authoritative documentation instead of duplicating a repository overview.

Limits: the evaluation is Python-focused, and task resolution does not capture every benefit of better maintainability or coordination.

### 3. Evaluation and Testing

#### Progress Mirage

[Progress Mirage](../papers/2607.25152-progress-mirage.pdf) is a preliminary pilot whose hypotheses were recorded before measurement but whose prescribed commit-hash freeze was not completed. It uses one open-ended conversion task family, one agent, one stronger judge, three repetitions per condition, and six cycles per repetition. Across 54 cycles, the agent claimed improvement every time, while 56% of changes had zero or negative externally measured improvement. A stronger in-band judge still accepted 40% of regressions and rejected 37.5% of true improvements. In the authors' channel-manipulation experiment, the out-of-band gate produced zero mirage by construction. On a bounded artifact-verifiable task, the stronger judge also reached zero mirage.

The correct boundary is important: an out-of-band evaluator is structurally valuable when success lives outside the agent's transcript or visible artifact. It is not automatically necessary when deterministic artifact checks already expose completion.

Limits: this is a narrow synthetic pilot with one task and model, only three repetitions per condition, and a deliberately simple external metric. Real-world measures can be noisy, delayed, incomplete, or hostile to temporary regressions required by large refactors. The paper's generator/evaluator separation is directly motivated; its broader auxiliary architecture proposals are not individually validated.

#### Agentic Property-Based Testing

[Agentic Property-Based Testing](../papers/2510.09907-agentic-property-based-testing.pdf) applies agent-generated property tests to 100 Python packages and 933 modules, producing 984 reports over 136.6 hours at a reported cost of $5,474. In a random manual sample of 50 reports, 56% were judged valid and 32% worth reporting. Among the top 21 reports selected by an LLM rubric, 18 were valid, 17 worth reporting, and three patches were merged.

Project interpretation: property and metamorphic testing can uncover failures that example tests miss, especially invariance and monotonicity violations. Generated properties must still be reviewed or validated against domain intent.

Limits: most reports were not manually reviewed, expected behavior can be ambiguous, false discoveries remain material, and the approach has meaningful compute cost and potential security implications.

### 4. Harnesses and Monitoring

#### LongHorizon-Harness

[LongHorizon-Harness](../papers/2608.01964-longhorizon-harness.pdf) uses a manager-executor-auditor loop. The manager owns structured task state without environment access; a fresh, budgeted executor is the only modifying role; and a fresh, read-only auditor verifies the environment. Only audit evidence updates state. The same underlying model may fill all roles, so independence comes mainly from context and permissions.

The paper reports substantial gains: Qwen 3.7-Plus rises from 51.8 to 80.7 on WeaveBench, from 69.7 to 77.2 on Terminal-Bench 2.1, and from 2.8 to 8.3 on OSWorld; Claude Opus 4.7 rises from 20.6 to 35.3 binary completion on a 34-task OSWorld subset, with partial score rising from 55.8 to 66.9. Token use increases 2.3x on WeaveBench and 3.6x on OSWorld, but falls 24% on Terminal-Bench. The auditor is the main overhead.

Project interpretation: this is the strongest architecture candidate for a first reproduction. Its value is likely highest when state management, drift, and recovery—not missing primitive coding skill—are the bottleneck.

Limits: this is a version-one preprint without a clear limitations section or clean component ablation. The benchmarks mix GUI and terminal tasks rather than long-term repository evolution. The full architecture should therefore be reproduced before being made a default.

The later replication-grade review narrows these claims further and records implementation differences in the [core-workflow synthesis](../reviews/core-workflow/SYNTHESIS.md).

#### LivePlan

[LivePlan](../papers/2608.06701-liveplan.pdf) separates deterministic trajectory monitoring from LLM recovery advice. Its blocking monitors detect premature patching, skipped patching, skipped validation, and thought/action oscillation. Nonblocking monitors detect prolonged navigation, reproduction, patching, or validation, plus repeated actions and revisits. Across 7,752 trajectories on SWE-bench Pro and Verified, it reports gains up to 15.24 percentage points and an average gain of 9.9 points, with low advisor cost. Removing the monitor or advisor degrades performance; periodic, untriggered advice creates more misleading interventions.

Project interpretation: implement the event taxonomy first as telemetry. Derive thresholds from observed trajectories, then test advisory and blocking policies separately.

The source workflow's example rules—such as “the same test fails three times” or “the same file is modified four times”—are reasonable hypotheses, but they are not LivePlan's evaluated rules. The paper's long-stagnation threshold was seven steps, selected from its own vanilla-trajectory distribution, and its maximum was five consecutive blocking interventions.

Limits: the taxonomy is tied to SWE-agent issue-resolution phases; thresholds may not transfer; runs are nondeterministic; and advisor calls can fail.

## Corrections to the Supplied Workflow

### Keep

- specifications tied to executable acceptance evidence;
- regression suites, properties, metamorphic checks, and architectural invariants;
- persistent, version-controlled task and decision state;
- small verified work units and clean handoffs;
- separation between code-writing and evidence-based acceptance;
- deterministic monitoring before LLM recovery advice;
- explicit preservation of the best-known verified state.

### Reframe

- **Milestone DAG:** useful representation and benchmark structure; an optional scheduling strategy until a local experiment shows benefit.
- **Out-of-band evaluation:** required when the real objective is external to the agent's view, not for every bounded task.
- **Independent auditor:** independence can be enforced through fresh context and read-only permissions; it need not always be a different model.
- **Paper reproduction:** one form of evidence-driven engineering, not an automatic guarantee that the result transfers to a new domain.

### Remove as Defaults

- universal numeric anti-loop limits copied without calibration;
- “10/10” rankings that imply a precision the studies do not provide;
- large generated repository summaries in `AGENTS.md`;
- the assumption that more agents or stricter plan compliance is inherently better;
- treating the executor's narrative, test selection, or self-review as the acceptance authority.

## Recommended First Implementation

Build the workflow in four layers, each independently testable.

### Layer 1: Evidence Contract

Each unit of work records:

- requirement and source;
- expected observable behavior;
- evaluator type and commands;
- baseline result;
- regression constraints;
- allowed temporary-regression or exploration policy;
- acceptance evidence and artifact locations.

Use three evaluator trust levels:

1. **Local deterministic:** tests, lint, type checks, invariants, reproducible artifact inspection.
2. **Isolated held-out:** hidden or read-only tests and benchmarks unavailable to the executor.
3. **World-state:** simulation, deployed behavior, user outcomes, hardware, or another external measurement channel.

### Layer 2: Verified State

Store requirements, decisions, artifacts, evaluator results, and state transitions in the repository or another append-only record. Raw conversation is diagnostic data, not project truth. Only passed evidence can mark a work item verified.

### Layer 3: Execution and Audit

For each work item:

1. a manager selects one ready item from verified state;
2. a fresh executor receives only the necessary map, contract, and evidence;
3. the executor makes the change and records claims;
4. a fresh, read-only auditor runs or inspects the declared evaluator;
5. the manager accepts, rejects, or replans based on audit evidence.

An explicit exploration mode may permit temporary regressions, but it must preserve the prior best-known state and end in a full comparison.

### Layer 4: Watchdog

First collect telemetry using LivePlan-inspired event categories. Do not intervene. After enough trajectories:

- estimate normal phase lengths and revisit distributions;
- label true stagnation and productive persistence;
- measure false alarms;
- test advisory recovery;
- enable blocking only when its net benefit is demonstrated.

## First Reproduction Experiment

Run an A/B evaluation before building a general orchestrator.

**Control:** the project's normal coding agent and existing instructions.

**Treatment:** evidence contract + persistent verified state + fresh executor + read-only auditor.

**Optional later arms:** reminders, milestone DAG scheduling, observe-only watchdog, advisory watchdog.

Use at least two repositories and multiple repeated runs because agent execution is nondeterministic. Include both bounded issue tasks and a multi-step evolution task.

Measure:

- complete task resolution and partial completion;
- regressions and false completion claims;
- human interventions;
- wall time, tokens, and monetary cost;
- evaluator failures and flaky results;
- maintainability review for accepted changes;
- recovery from an intentionally injected failed subtask.

The decision rule should be set before the experiment. For example: adopt a treatment only if it improves verified completion without increasing regressions and its cost per additional successful task is acceptable.

## Bottom Line

The research supports building Agentic Engineering around an evidence boundary, not around a more elaborate prompt. The immediate reusable artifact should be a small experimental protocol that can prove which interventions help. Once that foundation produces repeatable gains, the project can encode the winning pieces as schemas, skills, runners, watchdogs, or a full harness.

## Provenance

The exact local artifacts, page counts, titles, and SHA-256 values are recorded in [the paper manifest](../papers/manifest.json). The complete source classification, including supporting official resources, is in [the source index](../sources.md).
