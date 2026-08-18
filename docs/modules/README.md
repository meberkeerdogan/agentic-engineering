# Implementation Modules

Agentic Engineering was delivered as nine independent core modules. All nine pass their offline implementation gates. M10 is an optional later extension. Efficacy promotion is separate: experimental behavior becomes a default only after it beats the simpler baseline without unacceptable regressions.

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
       -> M10 Optional Learning Companion
```

## Module Status

| Module | Outcome | Promotion gate |
| --- | --- | --- |
| [M01 Core contracts](01-core-contracts.md) | Portable formats for specifications, evidence, state, and experiments | Schemas and examples pass automated validation |
| [M02 Active-spec compiler](02-active-spec-compiler.md) | One current contract from direct or revised requirements | Contract-equivalent histories compile to the same active behavior |
| [M03 Baseline and evaluators](03-baseline-and-evaluators.md) | Agentless-style baseline plus command, artifact, rubric, and world-state evaluator interfaces | A fixture task produces reproducible evidence without an autonomous loop |
| [M04 Verified state store](04-verified-state-store.md) | Append-only run state derived from evaluator evidence | Invalid transitions and unevidenced completion are rejected |
| [M05 Verified single-agent runner](05-verified-single-agent-runner.md) | Manager, fresh executor, and read-only auditor orchestration | Executor claims cannot mark work verified; only auditor evidence can |
| [M06 Experiment harness](06-experiment-harness.md) + [Codex CLI adapter](06b-codex-cli-adapter.md) + [private live pilot](06c-live-pilot-runner.md) + [clean environment](06d-clean-codex-environment.md) + [resumable batch runner](06e-resumable-batch-runner.md) + [live experiment bridge](06f-live-codex-experiments.md) + [representative task pack](06g-representative-task-pack.md) + [live trajectory capture](06h-live-trajectory-capture.md) + [representative sentinel](06i-representative-sentinel.md) + [multi-step evolution sentinel](06j-evolution-sentinel.md) | Repeatable control/treatment comparisons with safe live boundaries, budgets, durable progress, clean Codex execution, an offline-validated representative matrix, observe-only trajectory evidence, and staged live safety gates | Repeated runs report completion, regressions, false completion, cost, and time; executor claims remain untrusted |
| [M07 Optional interventions](07-optional-interventions.md) + [phase-memory evidence campaign](07d-phase-memory-campaign.md) + [memory safety sentinel](07d-phase-memory-sentinel.md) + [budgeted live campaign](07d-phase-memory-live-campaign.md) | Adaptive planning, memory, property testing, and observe-first watchdog; bounded memory passed its safety gate and has an offline-validated 18-cell live boundary | Each intervention beats the baseline on its declared target without unacceptable regressions |
| [M08 Paper reproduction toolkit](08-paper-reproduction.md) | Paper, lineage, environment, rubric, experiment, and deviation workflow | One selected paper claim is reproduced with traceable evidence and explicit scope limits |
| [M09 Isolated multi-agent runner](09-isolated-multi-agent.md) | Dependency-safe worktree delegation and integration | Isolation and integration pass offline; default promotion still requires beating the verified single-agent runner |
| [M10 Optional Learning Companion](10-learning-companion.md) | Fresh proposal-only teaching agent over bounded milestone evidence | Runtime adapters must preserve evidence binding and improve learning value enough to justify context, cost, and time |

## Execution Rule

The sequential implementation phase is complete. Future work should use the M06 harness to evaluate one bounded intervention at a time, preserve the verified single-agent baseline, and record evidence before changing defaults.
