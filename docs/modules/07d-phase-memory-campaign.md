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

The [budgeted live campaign](07d-phase-memory-live-campaign.md) has completed all nine canonical-rereading controls, all three low-pressure treatments, and the first supersession-pressure treatment. Every cell independently verified with no regressions, false completion, or intervention. Across the complete median block, treatment quality is equal while treatment used `20.18%` more credits and `3.74%` less time. In the first restock pair, memory correctly excluded the obsolete decision, but both arms passed and treatment used `36.71%` more credits and `4.48%` more time. This is correct retrieval behavior, not yet evidence of memory benefit. Five pressure-task treatments remain separately approval-gated.
