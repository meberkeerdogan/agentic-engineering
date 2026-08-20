# Phase-Memory Campaign: Cell 16

**Date:** 2026-08-20

**Model:** `gpt-5.6-luna` through the existing ChatGPT Codex login

**Batch:** `codex-memory-campaign-001`

**Cell:** Bounded phase-memory treatment, `roadmap-evolution`, seed `0`

## Result

The sixteenth campaign cell passed and started the eviction-pressure treatment block. A fresh plugin-free and MCP-free preflight succeeded, the task ran in an isolated workspace containing `workflow-phase-memory.md` but not `workflow-no-memory.md`, and independent evaluation accepted both implementation artifacts plus all six tests.

| Measure | Cell 16 | Per-cell ceiling |
| --- | ---: | ---: |
| Verified completion | 100% | required |
| Regressions | 0 | 0 |
| False completion | 0 | 0 |
| Estimated credits | 0.217543 | 0.5 |
| Wall time | 67.109 s | 300 s |
| Human interventions | 0 | 0 |

The measured turn used 116,741 input tokens, including 93,696 cached, 1,849 output tokens, and 230 reasoning tokens.

## Memory and trajectory

The workspace memory ledger exactly matched the source SHA-256 digest `bfd76819f32a2711aa824afbd02c0def77621956f093690ae67c0777f17bea79`. Its deterministic view retained and retrieved `roadmap-current`, `roadmap-evidence`, and `roadmap-failure`, while capacity eviction removed the unrelated `roadmap-distractor`. The agent followed the retained two-module plan and preserved the existing listing and completed-count behavior.

The privacy-safe trajectory contains eight events covering memory-aware inspection, baseline reproduction, a two-file patch, validation, final diff inspection, the executor claim, and a passing independent audit. The observe-only watchdog emitted zero signals and made no intervention. Review found no memory-attributable error.

## First eviction pair

| Measure | Control seed 0 | Treatment seed 0 | Treatment difference |
| --- | ---: | ---: | ---: |
| Verified completion | 1 / 1 | 1 / 1 | 0 |
| Regressions | 0 | 0 | 0 |
| Credits | 0.249623 | 0.217543 | -0.032080 (-12.85%) |
| Seconds | 79.750 | 67.109 | -12.641 (-15.85%) |

The treatment applied eviction correctly and completed more cheaply and quickly than its paired control. The control also passed, so this pair shows no completion benefit. Two repeated roadmap seeds remain necessary before interpreting the eviction block.

## Campaign state

The launcher paused after exactly one additional cell, as required:

- completed: `16 / 18`;
- measured cost so far: `3.507295 / 9.0` credits;
- measured model time so far: `1,059.500 / 5,400` seconds;
- human interventions: `0`;
- next declared cell: bounded phase-memory treatment, `roadmap-evolution`, seed `1`.

No later cell is authorized by this result. The next invocation requires a new explicit approval naming its task, seed, workflow arm, authenticated service, and `0.5`-credit/`300`-second ceilings.

## Evidence fingerprints

- Evaluation report: `8de6abf713a50f95809b29d59a507528d1afa50927cf75a44f2e91c2c7d35362`
- Memory view: `22acaeeb9261e0aa466de960fbf7d1e0f6ad1985471100e4d297a90fdd459594`
- Trajectory: `a61803cd0b49047866eb75c9796a62a6d3f8aefd681e3c364018b139ff2fe394`
- Watchdog report: `59eb72c7e55a03c5b3f8dea41db708c22fc3afce7ee38acd805caa16bb0b8ee9`
- Campaign plan: `6367dd78e47b2880239bb4b143484c3a028f5e5e151e7bbb528f4e1c4e43076f`
- Live configuration: `1f5ce84cb123d9a9f3d8764de3028fe566d3f943b58f3f3f0321ed31e3e2d5a3`
- Execution inputs: `1c461c40d8e35ee222851d080ed6217e8ad36940916d0a171876db85446d5307`
