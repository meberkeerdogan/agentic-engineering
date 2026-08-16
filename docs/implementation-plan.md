# Implementation Plan

Agentic Engineering will build a **verified adaptive engineering system**. It is not one giant autonomous loop. Each layer must beat a simpler baseline before becoming a default.

## Complete Workflow

```text
current user intent
    -> active specification
    -> simple baseline
    -> repository map and evidence contract
    -> bounded task execution
    -> deterministic checks
    -> independent read-only audit
    -> verified state update
    -> replan or continue
    -> final contract audit
```

The project will also use a research lifecycle:

```text
paper -> reproduce -> ablate -> measure -> extract primitive
      -> compose workflow -> benchmark again -> publish evidence
```

## What We Will Build

1. **Active specification:** compile changing requests into one current contract and clearly supersede old requirements. Inspired by SpecPath.
2. **Simple baseline:** use a bounded localization, implementation, and validation flow. Inspired by Agentless. Every more complex system must beat it.
3. **Evidence contract:** define acceptance checks, baseline results, regression rules, and evidence locations before implementation.
4. **Verified state:** store tasks, decisions, failures, artifacts, and evaluator results outside the conversation. Conversation text is not project truth.
5. **Verified single-agent runner:** a manager selects one task, a fresh executor changes code, and a fresh read-only auditor accepts or rejects it from evidence.
6. **Runtime control:** keep branching, retries, budgets, and state transitions in deterministic code. Retry failed subtasks instead of restarting everything.
7. **Planning and memory experiments:** compare static plans, adaptive dependency plans, and phase-aware memory. Adopt only the parts that improve results.
8. **Observe-first watchdog:** collect repeated-action, skipped-validation, and stagnation events before enabling advice or blocking.
9. **Paper reproduction toolkit:** extract claims and rubrics, follow paper lineage and reference code, reconstruct environments, run experiments, and record deviations.
10. **Isolated multi-agent runner:** only after the single-agent system works, parallelize independent tasks in isolated Git worktrees and integrate them with tests.
11. **Evaluation harness and live adapters:** run repeatable control/treatment comparisons across repositories and record completion, regressions, false completion, cost, time, and human intervention. Live adapters execute agents in isolated workspaces while independent evaluators retain verification authority.

## Research Decisions

### Use in the first implementation

- **Agentless:** defines the minimum baseline.
- **SpecPath:** motivates the active-specification compiler.
- **Progress Mirage:** motivates evidence-based acceptance instead of self-reported progress.
- **LongHorizon-Harness:** motivates fresh executor and read-only auditor roles.
- **Runtime-Structured Task Decomposition:** motivates deterministic control and subtask-level retries.
- **PaperBench, AutoReproduce, and EXP-Bench:** shape the research-reproduction workflow.
- **SWE-EVO, RoadmapBench, and SWE-Milestone:** shape long-horizon evaluation tasks and partial-progress metrics.
- **From Plan to Action and Evaluating AGENTS.md:** constrain plans and repository guidance to be small and task-specific.

### Test later, not default yet

- **CodePlan:** promising adaptive dependency planning, but evaluated on a limited task set.
- **PMCoder:** promising plan-memory coupling, but currently focused on issue resolution.
- **LivePlan:** useful monitoring taxonomy; thresholds must be calibrated locally.
- **Agentic Property-Based Testing:** useful complementary evaluator, but generated properties can be wrong.
- **CAID:** promising isolated multi-agent design, but coordination is added only after the single-agent baseline works.
- **CooperBench:** not an implementation template; it is evidence that unstructured multi-agent collaboration can hurt.

### Not planned now

- **Prometheus:** a repository knowledge graph is expensive and has not yet been shown to be our bottleneck.
- **ContextBench:** useful as an evaluation reference, not a component to implement.
- **TICoder:** overlaps with the evidence-contract and planning experiments; defer until those are measured.
- **SWE-agent interface reproduction:** useful historical evidence, but existing coding tools already provide a baseline interface.
- **Live-SWE-agent:** runtime self-modification expands the safety and evaluation surface too early.
- **Horizon Gap:** useful survey and vocabulary, but it is not a mechanism to reproduce.

## Delivery Order

Implementation is split into nine promotion-gated modules. See the [module dependency map](modules/README.md) for the delivery order and the detailed [M01 core-contract specification](modules/01-core-contracts.md).

Only one module is active at a time. The next module is specified in detail only after its dependency passes, so measurements can change later designs without forcing a large rewrite.
