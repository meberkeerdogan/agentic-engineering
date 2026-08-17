# Examples

This directory contains example contracts, fixtures, experiments, playbooks, workflows, and skills.

Good examples should be small, realistic, and easy to copy into another project.

Candidate examples:

- planning playbook
- implementation playbook
- test-fix workflow
- code-review playbook
- release-handoff playbook
- skill-driven review workflow

Current examples:

- [`planning-playbook.md`](planning-playbook.md)
- [`project-preferences.json`](project-preferences.json)
- [`active-spec.json`](active-spec.json)
- [`spec-history-direct.json`](spec-history-direct.json)
- [`spec-history-revised.json`](spec-history-revised.json)
- [`evidence-contract.json`](evidence-contract.json)
- [`verified-state.json`](verified-state.json)
- [`experiment-record.json`](experiment-record.json)
- [`experiment-observations.json`](experiment-observations.json): complete replay matrix for the M06 example.
- [`expected-experiment-report.json`](expected-experiment-report.json): deterministic M06 golden report.
- [`watchdog-trajectory.json`](watchdog-trajectory.json): M07a trajectory containing repeat, stagnation, oscillation, and phase-order failures.
- [`trajectory-source.json`](trajectory-source.json): redacted provenance shape connecting normalized trajectory steps to raw Codex JSONL lines.
- [`expected-watchdog-report.json`](expected-watchdog-report.json): deterministic observe-only M07a report.
- [`watchdog-labels.json`](watchdog-labels.json): synthetic labels for every signal in the watchdog fixture.
- [`watchdog-calibration.json`](watchdog-calibration.json): calibration manifest with explicit eligibility thresholds.
- [`expected-watchdog-calibration.json`](expected-watchdog-calibration.json): deterministic calibration-only golden report.
- [`expected-advisory-report.json`](expected-advisory-report.json): deterministic M07b fixture output filtered by synthetic calibration eligibility.
- [`dependency-plan.json`](dependency-plan.json): dependency graph with evidenced completion and failure states for M07c.
- [`expected-static-dependency-plan.json`](expected-static-dependency-plan.json) and [`expected-adaptive-dependency-plan.json`](expected-adaptive-dependency-plan.json): golden fixed-order and failure-aware planning views.
- [`phase-memory.json`](phase-memory.json) and [`expected-phase-memory.json`](expected-phase-memory.json): bounded M07d provenance and retrieval fixture plus golden view.
- [`property-testing.json`](property-testing.json) and [`expected-property-testing.json`](expected-property-testing.json): independently reviewed M07e property evidence and counterexample summary.
- [`fixture-task/`](fixture-task/): a prepared candidate, four-type evidence contract, and deterministic golden evaluation report for M03.
- [`live-pilot.json`](live-pilot.json): one private Codex control-run configuration for M06c.
- [`live-pilot-rates.json`](live-pilot-rates.json): dated external rates used to estimate the example run's subscription-credit usage.
- [`codex-environment.json`](codex-environment.json): clean-home and no-credit preflight policy for M06d.
- [`expected-codex-preflight-report.json`](expected-codex-preflight-report.json): portable shape plus the initial local prompt-footprint measurement.
- [`batch-experiment.json`](batch-experiment.json): a four-cell batch with two cells allowed per invocation.
- [`expected-batch-state.json`](expected-batch-state.json): golden paused state after the first two cells.
- [`live-experiment.json`](live-experiment.json): paid-run-gated launcher for the M06f Codex matrix.
- [`live-batch-experiment.json`](live-batch-experiment.json): two-cell budget with one live cell allowed per invocation.
- [`live-experiment-record.json`](live-experiment-record.json): one-task control versus verified-loop plumbing comparison.
- [`live-pilot-template/`](live-pilot-template/): a tiny deterministic median bug, tests, workflow, and independent evidence contract.
- [`evaluation-task-pack.json`](evaluation-task-pack.json): offline readiness requirements and evidence bindings for a representative workflow comparison.
- [`evaluation-task-pack-experiment.json`](evaluation-task-pack-experiment.json): three tasks, three seeds, two arms, and a predeclared efficacy decision rule.
- [`expected-task-pack-readiness.json`](expected-task-pack-readiness.json): deterministic proof that the representative matrix passes every offline gate without model execution.
- [`task-pack/`](task-pack/): deterministic multi-file feature and multi-step evolution repositories; the pack also reuses the median fixture.
- [`representative-sentinel-experiment.json`](representative-sentinel-experiment.json): one multi-file task, one seed, and both workflow arms for a safety sentinel rather than an efficacy claim.
- [`representative-sentinel-batch.json`](representative-sentinel-batch.json): two-cell sentinel with one cell per invocation, a 0.5-credit per-cell ceiling, and a 1-credit total ceiling.
- [`representative-sentinel-live.json`](representative-sentinel-live.json): paid-run-gated launcher for the representative sentinel.
- [`evolution-sentinel-experiment.json`](evolution-sentinel-experiment.json): one dependency-aware evolution task, one seed, and both workflow arms for the next safety sentinel.
- [`evolution-sentinel-batch.json`](evolution-sentinel-batch.json): two-cell evolution budget with one cell per invocation and a 0.75-credit per-cell ceiling.
- [`evolution-sentinel-live.json`](evolution-sentinel-live.json): separately approval-gated launcher for the evolution sentinel.
- [`multi-agent-run.json`](multi-agent-run.json) and [`multi-agent-fixture/`](multi-agent-fixture/): offline M09 dependency-wave and integration fixture.
- [`dependency-planning-campaign.json`](dependency-planning-campaign.json): offline-only M07c readiness contract with graph-shape and isolated-factor requirements.
- [`dependency-planning-experiment.json`](dependency-planning-experiment.json) and [`dependency-planning-task-pack.json`](dependency-planning-task-pack.json): three-task, three-seed static/adaptive comparison and its M06 evidence bindings.
- [`expected-planning-campaign-readiness.json`](expected-planning-campaign-readiness.json): deterministic proof of an 18-cell comparison with two divergent plans, one negative control, and no model authorization.
- The three representative task repositories now include dependency-plan inputs plus static and adaptive workflow policies with a byte-identical verified execution core.
- [`dependency-planning-sentinel-experiment.json`](dependency-planning-sentinel-experiment.json), [`dependency-planning-sentinel-batch.json`](dependency-planning-sentinel-batch.json), and [`dependency-planning-sentinel-live.json`](dependency-planning-sentinel-live.json): separately approval-gated two-cell static/adaptive safety sentinel with one cell per invocation.
- [`phase-memory-campaign.json`](phase-memory-campaign.json): offline-only M07d readiness contract with low-pressure, supersession, and eviction coverage plus an isolated memory-policy factor.
- [`phase-memory-experiment.json`](phase-memory-experiment.json) and [`phase-memory-task-pack.json`](phase-memory-task-pack.json): three-task, three-seed canonical-rereading versus bounded-memory comparison and its M06 evidence bindings.
- [`expected-phase-memory-campaign-readiness.json`](expected-phase-memory-campaign-readiness.json): deterministic proof of an 18-cell memory comparison with two pressure tasks, one negative control, and no model authorization.
- The three representative task repositories include the same immutable phase-memory ledger for both arms plus control and treatment workflows with a byte-identical verified execution core.
- [`phase-memory-sentinel-experiment.json`](phase-memory-sentinel-experiment.json), [`phase-memory-sentinel-batch.json`](phase-memory-sentinel-batch.json), and [`phase-memory-sentinel-live.json`](phase-memory-sentinel-live.json): separately approval-gated two-cell canonical-rereading/bounded-memory safety sentinel with one cell per invocation.
- [`phase-memory-live-batch.json`](phase-memory-live-batch.json) and [`phase-memory-live.json`](phase-memory-live.json): offline-validated 18-cell live boundary with one cell per invocation, a 0.5-credit/300-second per-cell ceiling, and a 9-credit/90-minute total ceiling.
