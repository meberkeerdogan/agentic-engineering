# Tests

The first implemented suite validates the M01 core schemas, examples, unique identifiers, and cross-references.

```powershell
uv run --group test pytest
```

Later modules will add workflow state-transition, evaluator, checkpoint, runner, and handoff tests.

`test_active_spec_compiler.py` verifies M02 history compilation, contract equivalence, canonical output, invalid-history rejection, and the command-line interface.
