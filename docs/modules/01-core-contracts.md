# M01: Core Contracts

**Status:** Implemented

## Why This Module Exists

The repository currently has one project-preferences schema but no shared format for the active specification, acceptance evidence, verified run state, or experiments. Every later runner would otherwise invent incompatible data structures.

## Deliverables

| File | Purpose |
| --- | --- |
| `schemas/active-spec.schema.json` | Current requirements and explicit supersession |
| `schemas/evidence-contract.schema.json` | Acceptance criteria, evaluators, baselines, and regression policy |
| `schemas/verified-state.schema.json` | Work items, decisions, evidence, and verified transitions |
| `schemas/experiment-record.schema.json` | Control/treatment configuration, metrics, runs, and adoption decision |
| `examples/*.json` | One valid example for each contract |
| `tests/test_core_schemas.py` | Schema validity, example validity, uniqueness, and cross-reference checks |

## Acceptance Criteria

1. All four schemas are valid JSON Schema Draft 2020-12 documents.
2. Every example validates against its schema with format checking enabled.
3. Duplicate requirement, criterion, evaluator, work-item, evidence, treatment, task, or metric IDs fail tests.
4. Evidence criteria cannot reference missing specification criteria or evaluators.
5. Verified-state dependencies and evidence references cannot point to missing records.
6. The module adds no runner, agent adapter, retry loop, database, network service, or multi-agent behavior.

## Test Command

```powershell
uv run --group test pytest
```

## Rollback

Revert the M01 files. No migrations or external state are involved.

## Next Module

M02 will compile a revision history into one active specification. Its key test will confirm that contract-equivalent requirement histories produce the same current requirements.

