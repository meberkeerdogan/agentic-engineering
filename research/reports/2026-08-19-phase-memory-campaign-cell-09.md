# Phase-Memory Campaign: Cell 09

**Date:** 2026-08-19

**Model:** `gpt-5.6-luna` through the existing ChatGPT Codex login

**Batch:** `codex-memory-campaign-001`

**Cell:** Canonical-rereading control, `roadmap-evolution`, seed `2`

## Result

The ninth campaign cell passed and completed both the three-seed roadmap control block and the full nine-cell control half. A fresh plugin-free and MCP-free preflight succeeded, the task ran in an isolated workspace containing `workflow-no-memory.md` but not `workflow-phase-memory.md`, and independent evaluation accepted both required files plus all six existing and roadmap-evolution tests.

| Measure | Cell 09 | Per-cell ceiling |
| --- | ---: | ---: |
| Verified completion | 100% | required |
| Regressions | 0 | 0 |
| False completion | 0 | 0 |
| Estimated credits | 0.230847 | 0.5 |
| Wall time | 78.266 s | 300 s |
| Human interventions | 0 | 0 |

The measured turn used 120,177 input tokens, including 95,744 cached, and 2,027 output tokens.

## Isolation and trajectory

The immutable memory ledger in the control workspace exactly matched the task source SHA-256 digest `bfd76819f32a2711aa824afbd02c0def77621956f093690ae67c0777f17bea79`. The treatment workflow was absent.

The privacy-safe trajectory contains eight events covering repository inspection, baseline reproduction, a two-file patch, validation, final diff inspection, the executor claim, and a passing independent audit. The observe-only watchdog emitted zero signals and made no intervention.

## Control-half baseline

All nine canonical-rereading controls independently verified with zero regressions, false completions, or human interventions.

| Task block | Verified | Mean credits | Mean seconds |
| --- | ---: | ---: | ---: |
| `median-fix` | 3 / 3 | 0.176605 | 59.974 |
| `restock-report` | 3 / 3 | 0.239873 | 75.193 |
| `roadmap-evolution` | 3 / 3 | 0.227641 | 71.250 |

The control half used `1.932357` credits and `619.251` seconds in total. The deterministic watchdog emitted four contextual false-positive stagnation alerts across the nine successful trajectories: three in the restock block and one in the roadmap block. It made no intervention.

This is the complete baseline, not evidence that phase memory helps. The nine treatment cells must now run against the same task and seed matrix.

## Campaign state

The launcher paused after exactly one additional cell, as required:

- completed: `9 / 18`;
- measured cost so far: `1.932357 / 9.0` credits;
- measured model time so far: `619.251 / 5,400` seconds;
- human interventions: `0`;
- next declared cell: bounded phase-memory treatment, `median-fix`, seed `0`.

No later cell is authorized by this result. The next invocation requires a new explicit approval naming its task, seed, workflow arm, authenticated service, and `0.5`-credit/`300`-second ceilings.

## Evidence fingerprints

- Evaluation report: `5a9de9de3eca6ba1b02ded16529bb11bc748af13780fe7a0321ec0fd25364512`
- Trajectory: `2e5d1331cd240cbdfee55686f23e3ef5354866b351618514c0be0077e216d1ea`
- Watchdog report: `7c260a18fe34a80c116a469c270b7fe7f4e18327942e5bd3d699c5f0510ea310`
- Campaign plan: `6367dd78e47b2880239bb4b143484c3a028f5e5e151e7bbb528f4e1c4e43076f`
- Live configuration: `1f5ce84cb123d9a9f3d8764de3028fe566d3f943b58f3f3f0321ed31e3e2d5a3`
- Execution inputs: `1c461c40d8e35ee222851d080ed6217e8ad36940916d0a171876db85446d5307`
