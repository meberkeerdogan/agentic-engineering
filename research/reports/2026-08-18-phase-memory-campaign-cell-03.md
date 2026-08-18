# Phase-Memory Campaign: Cell 03

**Date:** 2026-08-18

**Model:** `gpt-5.6-luna` through the existing ChatGPT Codex login

**Batch:** `codex-memory-campaign-001`

**Cell:** Canonical-rereading control, `median-fix`, seed `2`

## Result

The third campaign cell passed and completed the three-seed low-pressure control block. A fresh plugin-free and MCP-free preflight succeeded, the task ran in an isolated workspace containing `workflow-no-memory.md` but not `workflow-phase-memory.md`, and independent evaluation accepted the median tests and calculator artifact with no regression or false completion.

| Measure | Cell 03 | Per-cell ceiling |
| --- | ---: | ---: |
| Verified completion | 100% | required |
| Regressions | 0 | 0 |
| False completion | 0 | 0 |
| Estimated credits | 0.196425 | 0.5 |
| Wall time | 73.266 s | 300 s |
| Human interventions | 0 | 0 |

The measured turn used 105,327 input tokens, including 84,480 cached, and 1,665 output tokens.

## Isolation and trajectory

The immutable memory ledger in the control workspace exactly matched the campaign's `examples/live-pilot-template/phase-memory.json` SHA-256 digest `66e82a68394a5263913dd6d049dc882e75138578bd943d1938979fed8b032e91`. The treatment workflow was absent.

The privacy-safe trajectory contains eight events: navigation, baseline diff inspection, explicit reproduction, one-file patching, validation, final diff inspection, the executor claim, and a passing independent audit. The observe-only watchdog emitted zero signals and made no intervention.

## Campaign state

The launcher paused after exactly one additional cell, as required:

- completed: `3 / 18`;
- measured cost so far: `0.529814 / 9.0` credits;
- measured model time so far: `179.923 / 5,400` seconds;
- human interventions: `0`;
- next declared cell: canonical-rereading control, `restock-report`, seed `0`.

All three `median-fix` control seeds independently verified with zero regressions, false completions, watchdog signals, or human interventions. This establishes a stable low-pressure control sample but does not compare canonical rereading with bounded phase memory.

No later cell is authorized by this result. The next invocation requires a new explicit approval naming its task, seed, workflow arm, authenticated service, and `0.5`-credit/`300`-second ceilings.

## Evidence fingerprints

- Evaluation report: `34d1870900aeed91c76c93cc5ca9ef04fbd5835eae1a7a5124705d4f25bb3935`
- Trajectory: `ea200354016ffb7479f91fffd0ec96560f20571181be9a34de9775c31303755b`
- Watchdog report: `d7751879976768c1b1d4a12e8592c5530b0739c6d5a76b9ec5e8404f48ca9240`
- Campaign plan: `6367dd78e47b2880239bb4b143484c3a028f5e5e151e7bbb528f4e1c4e43076f`
- Live configuration: `1f5ce84cb123d9a9f3d8764de3028fe566d3f943b58f3f3f0321ed31e3e2d5a3`
- Execution inputs: `1c461c40d8e35ee222851d080ed6217e8ad36940916d0a171876db85446d5307`
