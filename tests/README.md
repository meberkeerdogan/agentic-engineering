# Tests

The offline suite validates all nine core modules plus the optional M10 extension, their schemas and examples, safety boundaries, deterministic reports, and integration fixtures.

```powershell
uv run --group test pytest
```

`test_active_spec_compiler.py` verifies M02 history compilation, contract equivalence, canonical output, invalid-history rejection, and the command-line interface.

`test_evaluators.py` verifies M03 command, artifact, rubric, and world-state evidence; golden-report determinism; regression detection; path containment; and the single-pass CLI.

`test_state_store.py` verifies M04 state transitions, dependency unlocking, report integrity, claim/evidence separation, retry behavior, hash-chain tamper detection, and schema-valid replay.

`test_runner.py` verifies M05 manager/executor/auditor separation, fresh executors per attempt, independent evidence, mismatch blocking, and rejection of executor-authored reports.

`test_experiments.py` verifies the M06 fixed matrix, deterministic golden report, independent false-completion derivation, paired aggregation, complete replay coverage, adapter preflight, evidence requirements, and command-line output.

`test_watchdog.py` verifies M07a observe-only signal detection, healthy-flow silence, threshold validation, immutable input, deterministic fingerprints, and command-line output.

`test_watchdog_calibration.py` verifies complete signal labelling, exact report binding, duplicate-case rejection, false-negative accounting, eligibility thresholds, safe manifest paths, deterministic aggregation, and command-line output.

`test_task_pack.py` verifies representative category coverage, repeated seeds, deterministic offline readiness, expected failing baselines, protected checks, workflow completeness, and zero model execution.

`test_trajectory_capture.py` verifies redacted JSONL normalization, workspace-state fingerprints, evidence provenance, schema validity, deterministic output, path containment, overwrite refusal, and observe-only watchdog compatibility.

`test_live_watchdog_calibration.py` verifies that real sentinel reports and labels remain privacy-safe, schema-valid, fingerprint-bound, calibration-only, and ineligible below the declared support and quality thresholds.

`test_advisory_watchdog.py` verifies fail-closed calibration binding, eligible-type filtering, deterministic advice, and permanently empty intervention and blocking surfaces.

`test_dependency_planning.py` verifies deterministic static and adaptive ordering, ready-frontier selection, transitive failure blocking, cycle rejection, and read-only outputs.

`test_planning_campaign.py` verifies the three-repository M07c comparison, shared workflow-core isolation, deterministic static/adaptive plan evidence, negative-control coverage, schema-valid golden readiness, and the prohibition on model authorization.

`test_live_experiments.py` also runs the M07c two-cell launcher against an offline Codex double, proving pause/resume behavior, per-cell budgets, independent evaluation, and selected-policy isolation without authenticated execution.

`test_phase_memory.py` verifies immutable provenance, safe supersession, deterministic per-phase bounds, phase/task-aware retrieval, and read-only output.

`test_property_testing.py` verifies independent proposal review, rejection of invented properties, read-only evidence requirements, counterexample follow-up, and no generated-code execution.

`test_paper_reproduction.py` verifies hash-bound paper lineage, contained trusted execution, deterministic observations, rubric scoring, deviations, schema validity, and fail-closed tampering.

`test_multi_agent.py` verifies parallel independent worktrees, dependency commit delivery, declared-path enforcement, clean-source preservation, deterministic integration, final validation, schemas, and cycle rejection.

`test_learning_companion.py` verifies bounded milestone prompts, fresh companion instances, disabled no-agent behavior, evidence-bound focus files, preservation of failed experiments, deterministic proposal reports, empty engineering-authority surfaces, and the CLI.
