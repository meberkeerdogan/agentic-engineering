# Examples

This directory will hold example playbooks, workflows, and skills.

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
