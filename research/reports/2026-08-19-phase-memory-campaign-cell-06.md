# Phase-Memory Campaign: Cell 06

**Date:** 2026-08-19

**Model:** `gpt-5.6-luna` through the existing ChatGPT Codex login

**Batch:** `codex-memory-campaign-001`

**Cell:** Canonical-rereading control, `restock-report`, seed `2`

## Result

The sixth campaign cell passed and completed the three-seed supersession-pressure control block. A fresh plugin-free and MCP-free preflight succeeded, the task ran in an isolated workspace containing `workflow-no-memory.md` but not `workflow-phase-memory.md`, and independent evaluation accepted both required files plus all seven existing and restock tests.

| Measure | Cell 06 | Per-cell ceiling |
| --- | ---: | ---: |
| Verified completion | 100% | required |
| Regressions | 0 | 0 |
| False completion | 0 | 0 |
| Estimated credits | 0.239883 | 0.5 |
| Wall time | 75.297 s | 300 s |
| Human interventions | 0 | 0 |

The measured turn used 145,743 input tokens, including 121,856 cached, and 1,984 output tokens.

## Isolation and trajectory

The immutable memory ledger in the control workspace exactly matched the task source SHA-256 digest `e25068f66c1a0d5caf5fe2e6e8e894f5e5d43b62bd170f32908538c39fb02108`. The treatment workflow was absent.

The privacy-safe trajectory contains ten events. The observe-only watchdog emitted two `stagnation` signals and made no intervention. Manual review classified both as contextual false positives:

- the first covered normal repository inspection and baseline testing before the patch;
- the second covered the completed patch followed by tests and two read-only diff inspections.

Repository state remaining unchanged during investigation or validation did not indicate that the agent was stuck.

## Restock control block

All three restock control seeds independently verified with zero regressions, false completions, or human interventions. Their mean measured cost was `0.239873` credits and their mean model time was `75.193` seconds. Across the three trajectories, the deterministic watchdog emitted three contextual false-positive stagnation alerts: one on seed `0`, none on seed `1`, and two on seed `2`.

This is a stable canonical-rereading baseline under supersession pressure. It does not yet show whether bounded phase memory is better or worse.

## Campaign state

The launcher paused after exactly one additional cell, as required:

- completed: `6 / 18`;
- measured cost so far: `1.249434 / 9.0` credits;
- measured model time so far: `405.501 / 5,400` seconds;
- human interventions: `0`;
- next declared cell: canonical-rereading control, `roadmap-evolution`, seed `0`.

No later cell is authorized by this result. The next invocation requires a new explicit approval naming its task, seed, workflow arm, authenticated service, and `0.5`-credit/`300`-second ceilings.

## Evidence fingerprints

- Evaluation report: `06befe8af481dd3cb5d0e43c02474f726b1be27a2b50b5bef3d682085a010048`
- Trajectory: `7946a3aa4bd62cb85c08a2c416248675745a7b2d654fcba40769f5cb532afeb4`
- Watchdog report: `9c25455df2abe22ffdc41c1d4c75db77631794bb550d92f5a80f4cbffce1a7e6`
- Campaign plan: `6367dd78e47b2880239bb4b143484c3a028f5e5e151e7bbb528f4e1c4e43076f`
- Live configuration: `1f5ce84cb123d9a9f3d8764de3028fe566d3f943b58f3f3f0321ed31e3e2d5a3`
- Execution inputs: `1c461c40d8e35ee222851d080ed6217e8ad36940916d0a171876db85446d5307`
