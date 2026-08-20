# M06g: Representative Task Pack

**Status:** Implemented

**Evidence boundary:** This is a plumbing and safety pack, not a convincing long-task efficacy benchmark. The starting repositories contain only 8-12 lines of source code, and the completed live comparisons reached a ceiling. The full [long-task research review](../../research/reviews/long-task/SYNTHESIS.md) and [harder test design](../../research/reviews/long-task/HARDER_TEST_DESIGN.md) define its replacement.

## Purpose

The first live comparison proved that the execution plumbing works, but one easy task and one seed cannot measure workflow efficacy. M06g prepares a larger comparison without spending credits.

The committed pack contains:

- one bounded bug fix;
- one feature that requires coordinated changes across two modules;
- one multi-step dependency-aware evolution task;
- three repeated seed labels;
- the existing bounded control and verified-loop treatment.

This produces an 18-cell matrix: two arms multiplied by three tasks and three seeds.

## Offline readiness boundary

The validator rejects a pack unless:

- the experiment contains every required task category and enough distinct repositories and seeds;
- every task has its specification, evidence contract, and every arm's workflow file;
- repository templates contain no filesystem links or Git metadata;
- every initial baseline fails only its expected task evaluator;
- previously passing protected checks still pass;
- baseline command evaluators use only the standard-library unittest runner;
- repository contents, the pack, and the experiment plan receive deterministic fingerprints.

Baseline checks run on temporary copies. The validator never invokes Codex or another model and records `model_calls_performed: false` in its report.

Task repositories and their unit tests are trusted local inputs. Python tests can execute code; this readiness check prevents arbitrary evaluator command arrays but is not an operating-system sandbox for malicious test files.

## Run

```powershell
uv run python -m agentic_engineering.task_pack `
  examples/evaluation-task-pack.json `
  --output task-pack-readiness.json
```

## Promotion gate

- Three representative categories are present across three repositories.
- Three seeds produce a fixed 18-cell plan.
- All initial failures and protected baselines match their declarations.
- Test-only known solutions make every task pass its independent evidence contract.
- Repeated validation produces the same report fingerprint.
- Invalid baselines, missing workflows, insufficient seeds, links, and path escapes fail closed.
- The complete repository test suite remains offline.

M06g does not authorize the 18 live cells. A later paid batch must first declare worst-case credit and time budgets and requires explicit user approval.

Do not rerun this pack to claim long-task efficacy. Keep it as a fast integration check while the Level 1 multi-target and Level 2 continuous-evolution tasks are implemented offline.
