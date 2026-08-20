# M07d: Phase-Memory Evidence Campaign

**Status:** Offline-ready and budgeted; no model execution authorized

## Purpose

This campaign tests whether deterministic, bounded phase-aware memory improves verified coding outcomes compared with canonical file rereading. Both arms receive the same task repository, active specification, evidence contract, immutable memory ledger, and verified execution core. The marked memory-policy block is the only workflow difference.

The prepared M06 matrix has two arms, three task categories, and three repeated seed labels, for 18 cells:

- a small median fix with no supersession or eviction, used as a low-pressure negative control;
- a multi-file restock feature whose newer decision supersedes an obsolete implementation choice;
- a multi-step roadmap evolution whose phase capacity evicts an unrelated distractor.

This design tests retrieval policy rather than giving the treatment extra facts. Every retrieved summary remains subordinate to its referenced canonical file.

## Offline readiness boundary

The `memory_campaign` validator:

- reuses M06 task-pack checks to prove each initial baseline fails only its expected evaluator;
- verifies three repositories, three seeds, two arms, standard metrics, and a predeclared adoption rule;
- requires byte-identical execution cores and one isolated control/treatment memory policy across all tasks;
- builds each M07d memory view locally and binds its deterministic fingerprint;
- checks expected retrieval, supersession, eviction, current-task evidence, and every evidence reference;
- requires one low-pressure negative control plus supersession and eviction pressure cases;
- rejects path escapes, filesystem links, missing evidence, changed expectations, side effects, and model authorization;
- records `model_calls_performed: false` and `paid_execution_authorized: false`.

It proves that the comparison is well formed. It does not prove memory is beneficial and does not authorize a paid run.

## Run

```powershell
uv run python -m agentic_engineering.memory_campaign `
  examples/phase-memory-campaign.json `
  --project-root . `
  --output phase-memory-campaign-readiness.json
```

## Next gate

The [two-cell phase-memory safety sentinel](07d-phase-memory-sentinel.md) completed within its hard limits. Both arms independently verified without memory-attributable errors. Bounded memory was cheaper and faster in the single pair, but completion was identical and two cells cannot establish efficacy.

The [budgeted live campaign](07d-phase-memory-live-campaign.md) has completed 17 of 18 cells. Every completed cell independently verified with no regressions, false completion, or intervention. Both roadmap treatments correctly evicted the distractor and both arms passed. Seed-level efficiency directions were opposite; across two roadmap pairs, treatment cost is `0.22%` lower and time is `1.65%` lower. The final eviction-pressure treatment remains separately approval-gated.
