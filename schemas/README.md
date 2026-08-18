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
- [`trajectory.schema.json`](trajectory.schema.json): ordered, evidenced coding-agent events with external state fingerprints.
- [`trajectory-source.schema.json`](trajectory-source.schema.json): redacted JSONL provenance for captured live trajectory events.
- [`watchdog-report.schema.json`](watchdog-report.schema.json): deterministic observe-only signals with explicit thresholds and no interventions.
- [`watchdog-labels.schema.json`](watchdog-labels.schema.json): complete human labels for detected signals and reviewer-recorded misses.
- [`watchdog-calibration.schema.json`](watchdog-calibration.schema.json): calibration policy and labelled case references.
- [`advisory-report.schema.json`](advisory-report.schema.json): calibration-bound experimental advice with structurally empty intervention and blocking surfaces.
- [`dependency-plan.schema.json`](dependency-plan.schema.json): dependency tasks, priorities, runtime evidence, and current states for planning experiments.
- [`dependency-plan-report.schema.json`](dependency-plan-report.schema.json): deterministic static or adaptive plan views with no execution side effects.
- [`phase-memory.schema.json`](phase-memory.schema.json): immutable phase-tagged entries, provenance, supersession, capacity, and retrieval query.
- [`phase-memory-report.schema.json`](phase-memory-report.schema.json): bounded retained and retrieved memory with no write side effects.
- [`property-testing.schema.json`](property-testing.schema.json): agent proposals, independent reviews, and read-only external property results.
- [`property-testing-report.schema.json`](property-testing-report.schema.json): accepted/rejected properties and evidenced counterexamples requiring follow-up.
- [`paper-reproduction.schema.json`](paper-reproduction.schema.json): paper, claim, lineage, environment, experiment, rubric, and deviation contract.
- [`paper-reproduction-report.schema.json`](paper-reproduction-report.schema.json): hash-bound claim-level reproduction results with explicit scope.
- [`multi-agent-run.schema.json`](multi-agent-run.schema.json): dependency DAG, explicit adapters, concurrency, path boundaries, and final validation.
- [`multi-agent-report.schema.json`](multi-agent-report.schema.json): worktree commits, waves, integration revision, and hashed validation evidence.
- [`watchdog-calibration-report.schema.json`](watchdog-calibration-report.schema.json): per-signal precision, recall, false-alarm rate, and advisory-experiment eligibility.
- [`live-pilot.schema.json`](live-pilot.schema.json): one isolated Codex control-cell configuration.
- [`usage-rates.schema.json`](usage-rates.schema.json): a dated, externally sourced model-usage rate card.
- [`codex-environment.schema.json`](codex-environment.schema.json): clean-home isolation and no-credit preflight policy.
- [`codex-preflight-report.schema.json`](codex-preflight-report.schema.json): redacted evidence that a live Codex environment passed its gates.
- [`batch-experiment.schema.json`](batch-experiment.schema.json): immutable matrix references, invocation size, and worst-case budgets.
- [`batch-state.schema.json`](batch-state.schema.json): resumable per-cell progress, observations, failures, and accumulated usage.
- [`live-experiment.schema.json`](live-experiment.schema.json): model, environment, rate-card, and evidence bindings for a live Codex batch.
- [`task-pack.schema.json`](task-pack.schema.json): representative task categories, repeated-run requirements, evidence bindings, and expected failing baselines.
- [`task-pack-readiness.schema.json`](task-pack-readiness.schema.json): fingerprinted proof that a task pack is ready without model execution.
- [`planning-campaign.schema.json`](planning-campaign.schema.json): M07c task-pack binding, graph-shape coverage, isolated workflow factor, and expected planning behavior.
- [`planning-campaign-readiness.schema.json`](planning-campaign-readiness.schema.json): fingerprinted static/adaptive campaign readiness with explicit zero-execution authorization.
- [`memory-campaign.schema.json`](memory-campaign.schema.json): M07d task-pack binding, memory-pressure coverage, isolated workflow factor, and expected bounded retrieval behavior.
- [`memory-campaign-readiness.schema.json`](memory-campaign-readiness.schema.json): fingerprinted canonical-rereading/bounded-memory campaign readiness with explicit zero-execution authorization.
- [`learning-milestone.schema.json`](learning-milestone.schema.json): bounded verified facts, decisions, failed experiments, learner goals, and focus references for one meaningful stage.
- [`learning-companion-submission.schema.json`](learning-companion-submission.schema.json): structured lesson, interpretation, exercise, review questions, and learning-path proposal from a teaching agent.
- [`learning-companion-report.schema.json`](learning-companion-report.schema.json): fingerprint-bound proposal with structurally empty engineering mutation and verification surfaces.

The core schema module and its validation rules are documented in [M01: Core Contracts](../docs/modules/01-core-contracts.md). The experiment schemas are implemented by [M06: Experiment Harness](../docs/modules/06-experiment-harness.md).
