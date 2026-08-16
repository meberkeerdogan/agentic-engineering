# Tests

The first implemented suite validates the M01 core schemas, examples, unique identifiers, and cross-references.

```powershell
uv run --group test pytest
```

Later modules will add workflow state-transition, evaluator, checkpoint, runner, and handoff tests.

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
