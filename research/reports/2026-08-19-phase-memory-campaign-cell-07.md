# Phase-Memory Campaign: Cell 07

**Date:** 2026-08-19

**Model:** `gpt-5.6-luna` through the existing ChatGPT Codex login

**Batch:** `codex-memory-campaign-001`

**Cell:** Canonical-rereading control, `roadmap-evolution`, seed `0`

## Result

The seventh campaign cell passed and started the eviction-pressure control block. A fresh plugin-free and MCP-free preflight succeeded, the task ran in an isolated workspace containing `workflow-no-memory.md` but not `workflow-phase-memory.md`, and independent evaluation accepted both required files plus all six existing and roadmap-evolution tests.

| Measure | Cell 07 | Per-cell ceiling |
| --- | ---: | ---: |
| Verified completion | 100% | required |
| Regressions | 0 | 0 |
| False completion | 0 | 0 |
| Estimated credits | 0.249623 | 0.5 |
| Wall time | 79.750 s | 300 s |
| Human interventions | 0 | 0 |

The measured turn used 139,015 input tokens, including 112,896 cached, and 2,086 output tokens.

## Isolation and trajectory

The immutable memory ledger in the control workspace exactly matched the task source SHA-256 digest `bfd76819f32a2711aa824afbd02c0def77621956f093690ae67c0777f17bea79`. The treatment workflow was absent.

The privacy-safe trajectory contains nine events covering repository inspection, baseline reproduction, a two-file patch, validation, the executor claim, and a passing independent audit. The observe-only watchdog emitted one `stagnation` signal because four useful inspection and reproduction events occurred before editing. Manual review classified it as a contextual false positive. The watchdog made no intervention.

## Campaign state

The launcher paused after exactly one additional cell, as required:

- completed: `7 / 18`;
- measured cost so far: `1.499057 / 9.0` credits;
- measured model time so far: `485.251 / 5,400` seconds;
- human interventions: `0`;
- next declared cell: canonical-rereading control, `roadmap-evolution`, seed `1`.

This first roadmap control run establishes a valid baseline for the task that will later test bounded-memory eviction. It does not yet compare canonical rereading with bounded phase memory.

No later cell is authorized by this result. The next invocation requires a new explicit approval naming its task, seed, workflow arm, authenticated service, and `0.5`-credit/`300`-second ceilings.

## Evidence fingerprints

- Evaluation report: `e3505f1532002434af2ee7bfa3abf2b9e884f2b2a063b7fd4c358950c45e2153`
- Trajectory: `ed1fc1beeb237d8f36a83ef8b5aa1060bd3cbd4fa911b7122bf1c2f183d9528d`
- Watchdog report: `b696bfd291ebfa5e263430a5999231eb4cb8ddbc1a283ef6dd806ae0562afc3e`
- Campaign plan: `6367dd78e47b2880239bb4b143484c3a028f5e5e151e7bbb528f4e1c4e43076f`
- Live configuration: `1f5ce84cb123d9a9f3d8764de3028fe566d3f943b58f3f3f0321ed31e3e2d5a3`
- Execution inputs: `1c461c40d8e35ee222851d080ed6217e8ad36940916d0a171876db85446d5307`
