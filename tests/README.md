# Tests

The first implemented suite validates the M01 core schemas, examples, unique identifiers, and cross-references.

```powershell
uv run --group test pytest
```

Later modules will add workflow state-transition, evaluator, checkpoint, runner, and handoff tests.

`test_active_spec_compiler.py` verifies M02 history compilation, contract equivalence, canonical output, invalid-history rejection, and the command-line interface.

`test_evaluators.py` verifies M03 command, artifact, rubric, and world-state evidence; golden-report determinism; regression detection; path containment; and the single-pass CLI.

`test_state_store.py` verifies M04 state transitions, dependency unlocking, report integrity, claim/evidence separation, retry behavior, hash-chain tamper detection, and schema-valid replay.
