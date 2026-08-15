# Schemas

Shared schemas describe portable playbook, skill, workflow, and output data.

Candidate schemas include playbook definitions, skill manifests, workflow state, evaluator results, and handoff records.

Current schemas:

- [`project-preferences.schema.json`](project-preferences.schema.json): explicit human preferences gathered during project onboarding.
- [`active-spec.schema.json`](active-spec.schema.json): the current, authoritative requirements contract.
- [`spec-history.schema.json`](spec-history.schema.json): a base specification and ordered operations that compile into an active contract.
- [`evidence-contract.schema.json`](evidence-contract.schema.json): acceptance criteria, evaluators, baselines, and regression policy.
- [`evaluation-report.schema.json`](evaluation-report.schema.json): deterministic criterion, evaluator, and regression evidence from one baseline run.
- [`verified-state.schema.json`](verified-state.schema.json): evidence-backed work-item and run state.
- [`state-event.schema.json`](state-event.schema.json): hash-chained append-only events that reduce to verified state.
- [`experiment-record.schema.json`](experiment-record.schema.json): reproducible control/treatment experiment records.
- [`experiment-observations.schema.json`](experiment-observations.schema.json): externally measured replay observations for every declared experiment cell.
- [`experiment-report.schema.json`](experiment-report.schema.json): deterministic run matrix, arm summaries, and paired treatment/control comparisons.

The core schema module and its validation rules are documented in [M01: Core Contracts](../docs/modules/01-core-contracts.md). The experiment schemas are implemented by [M06: Experiment Harness](../docs/modules/06-experiment-harness.md).
