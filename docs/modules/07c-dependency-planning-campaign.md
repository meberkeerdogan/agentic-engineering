# M07c: Dependency-Planning Evidence Campaign

**Status:** Offline-ready; no model execution authorized

## Purpose

This campaign tests one question: does adaptive, evidence-driven dependency planning improve verified coding outcomes compared with a fixed topological plan when the rest of the workflow is unchanged?

The prepared M06 matrix has two arms, three task types, and three repeated seed labels, for 18 cells:

- a chain-shaped median fix, used as a negative control where both planners produce the same order;
- a fan-out/fan-in restock feature where priority changes the ready-task order;
- a diamond-shaped roadmap evolution where priority changes the two independent branches.

Both arms use the same verified execution core. The validator removes the marked planning-policy block and requires the remaining workflow text to have one shared fingerprint across every task. It also requires one identical static policy and one identical adaptive policy across all repositories. This isolates planning policy from unrelated prompt changes.

## Offline readiness boundary

The campaign validator:

- reuses M06 task-pack checks to prove all initial baselines fail only their expected evaluator and protected behavior still passes;
- verifies the three repositories, three seeds, two arms, standard metrics, and predeclared adoption rule;
- executes M07c static and adaptive planning locally and binds their deterministic report fingerprints;
- requires two genuinely divergent plans and one non-divergent negative control;
- verifies every declared plan evidence file exists;
- rejects path escapes, filesystem links, workflow-factor drift, changed plan expectations, and any readiness manifest that permits model execution;
- records both `model_calls_performed: false` and `paid_execution_authorized: false`.

It proves that the comparison is well formed. It does not prove adaptive planning is better, and it does not authorize any live cell.

## Run

```powershell
uv run python -m agentic_engineering.planning_campaign `
  examples/dependency-planning-campaign.json `
  --project-root . `
  --output planning-campaign-readiness.json
```

## Next gate

Before a live run, create a separately reviewed batch and launcher with explicit per-cell and total credit/time ceilings. Start with one matched control/treatment sentinel, inspect its independent evaluations and trajectories, then decide whether to authorize the remaining repeated-seed matrix. Preparing this campaign grants no such approval.
