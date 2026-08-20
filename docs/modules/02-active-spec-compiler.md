# M02: Active-Spec Compiler

**Status:** Implemented

## Why This Module Exists

Long projects accumulate corrections, replacements, and scope changes. Sending the entire conversation back to an agent makes obsolete instructions look current. This module compiles an ordered revision history into one deterministic active specification.

The detailed [SpecPath dossier](../../research/reviews/core-workflow/specpath.md) supports testing path sensitivity, but its proposed explicit contract ledger was not evaluated as an intervention. M02 is therefore an **adaptation**: it compiles trusted structured operations and does not claim to infer the active contract from natural-language conversation. See the [core synthesis](../../research/reviews/core-workflow/SYNTHESIS.md).

## Inputs and Outputs

- `schemas/spec-history.schema.json` defines a base active specification plus ordered revision operations.
- `compile_history()` applies the revisions and returns an `active-spec` document.
- Superseded requirements remain in the compiled document for traceability.
- `behavioral_contract()` removes provenance and superseded requirements so two histories can be compared by current behavior.
- `behavior_fingerprint()` provides a stable SHA-256 identifier for that current behavior.

Supported revisions can set the objective or status, add or remove scope values, add sources, upsert requirements, and explicitly supersede requirements. Unknown operations, missing supersession targets, duplicate revision IDs, time-travel ordering, supersession cycles, and a result with no active requirements are rejected.

## Example

```powershell
uv run python -m agentic_engineering examples/spec-history-revised.json --output active-spec.json
```

Use `--behavior-only` to emit only the current behavioral contract or `--fingerprint` to emit its stable hash.

## Promotion Gate

The direct and revised example histories must compile to identical active behavior and the same behavior fingerprint, even though the revised artifact retains its superseded requirement lineage.

This local equivalence fixture is not a SpecPath reproduction. A future efficacy test must hold repository, verifier, agent, budget, and final contract fixed across direct, duplicate, split, override, and cancellation histories, then report direct competence and paired path violations separately.

## Test Command

```powershell
uv run --group test pytest
```

## Rollback

Revert the M02 compiler, history schema, examples, tests, and documentation. The compiler has no external state or migrations.

## Next Module

[M03](03-baseline-and-evaluators.md) implements a simple agentless-style baseline and read-only evaluator interfaces that produce reproducible evidence for fixture tasks.
