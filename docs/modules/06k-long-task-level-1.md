# M06k: Level 1 Multi-Target Fixture

**Status:** Implemented offline

## Why this module exists

The earlier comparison tasks are useful safety checks, but they start from only 8-12 lines of source code. Every live run completed them. This fixture creates enough connected work to reveal partial progress and integration failures before another paid experiment.

## What it contains

The agent-visible repository has nine Python source files and more than 500 source lines. One upgrade defines five named targets across inventory, allocation, shipping, reporting, and the service layer.

The hidden evaluator is stored outside the repository template. Offline validation copies it into a temporary evaluation candidate after the working repository is prepared. The agent-visible template therefore contains the specification and visible regression tests, but not the hidden checks or oracle patch.

The known-good oracle must pass all five target groups and the protected behavior suite. The untouched starting point must fail all target groups while keeping protected behavior green. Both reports must be deterministic.

## Evidence boundary

This proves that the fixture is internally valid and that the evaluator can measure partial progress. It does not prove that an agent can solve the task or that one workflow is better. A later held-out pilot must establish useful difficulty without a complete ceiling or floor.

## Test command

```powershell
python -m pytest tests/test_long_task_fixtures.py
```

## Rollback

Remove the Level 1 template, its external evaluator and oracle, this module note, and `tests/test_long_task_fixtures.py`. Target scoring remains independently useful.
