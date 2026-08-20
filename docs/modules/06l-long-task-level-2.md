# M06l: Level 2 Continuous Evolution Fixture

**Status:** Implemented offline

## Why this module exists

Solving five changes separately does not prove that an agent can keep one project correct over time. This module tests the same milestone once from a correct earlier state and once in a repository that preserves all earlier work. The difference is the continuous-versus-isolated gap.

## What it validates

The fixture streams five milestones over the 749-line fulfillment project. It has three independent branches, one dependent allocation milestone, and a final integration milestone. Only the current specification is copied into the working repository; future specifications, hidden tests, and oracle patches remain outside.

For every milestone, the validator proves:

1. the target fails before its patch while all earlier behavior passes;
2. the isolated oracle passes from the correct prior state;
3. the continuous oracle passes in the persistent repository;
4. isolated and continuous oracle states are identical;
5. an intentional omission of the first milestone is detected as a later regression.

## Evidence boundary

The zero gap on oracle paths proves that the chain itself is consistent. The omission probe proves that the evaluator can detect an inherited failure. Neither result measures an agent yet. Real workflow value requires held-out tasks and matched agent runs.

## Test command

```powershell
python -m pytest tests/test_milestone_chain.py
```

## Rollback

Remove the milestone-chain validator, schemas, chain manifest, split oracle patches, tests, and this module note. Level 1 remains independently usable.
