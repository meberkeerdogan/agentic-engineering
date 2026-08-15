# Implementation Modules

Agentic Engineering is delivered as independent modules. A module is promoted only when its acceptance tests pass and its output is useful without unfinished later modules.

## Dependency Map

```text
M01 Core contracts
  -> M02 Active-spec compiler
  -> M03 Baseline and evaluators
  -> M04 Verified state store
  -> M05 Verified single-agent runner
  -> M06 Experiment harness
       -> M07 Optional interventions
       -> M08 Paper reproduction toolkit
       -> M09 Isolated multi-agent runner
```

## Module Backlog

| Module | Outcome | Promotion gate |
| --- | --- | --- |
| [M01 Core contracts](01-core-contracts.md) | Portable formats for specifications, evidence, state, and experiments | Schemas and examples pass automated validation |
| [M02 Active-spec compiler](02-active-spec-compiler.md) | One current contract from direct or revised requirements | Contract-equivalent histories compile to the same active behavior |
| [M03 Baseline and evaluators](03-baseline-and-evaluators.md) | Agentless-style baseline plus command, artifact, rubric, and world-state evaluator interfaces | A fixture task produces reproducible evidence without an autonomous loop |
| [M04 Verified state store](04-verified-state-store.md) | Append-only run state derived from evaluator evidence | Invalid transitions and unevidenced completion are rejected |
| [M05 Verified single-agent runner](05-verified-single-agent-runner.md) | Manager, fresh executor, and read-only auditor orchestration | Executor claims cannot mark work verified; only auditor evidence can |
| M06 Experiment harness | Repeatable control/treatment comparisons | Repeated runs report completion, regressions, false completion, cost, and time |
| M07 Optional interventions | Adaptive planning, memory, property testing, and observe-first watchdog | Each intervention beats the baseline on its declared target without unacceptable regressions |
| M08 Paper reproduction toolkit | Paper, lineage, environment, rubric, experiment, and deviation workflow | One selected paper is reproduced with traceable evidence |
| M09 Isolated multi-agent runner | Dependency-safe worktree delegation and integration | It beats the verified single-agent runner on suitable parallel tasks |

## Execution Rule

Only one module is active at a time. Work on the next module begins after the current module passes its promotion gate. Later module specifications are intentionally brief until measurements from their dependencies are available.
