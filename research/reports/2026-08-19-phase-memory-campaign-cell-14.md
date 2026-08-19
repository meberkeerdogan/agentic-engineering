# Phase-Memory Campaign: Cell 14

**Date:** 2026-08-19

**Model:** `gpt-5.6-luna` through the existing ChatGPT Codex login

**Batch:** `codex-memory-campaign-001`

**Cell:** Bounded phase-memory treatment, `restock-report`, seed `1`

## Result

The fourteenth campaign cell passed. A fresh plugin-free and MCP-free preflight succeeded, the task ran in an isolated workspace containing `workflow-phase-memory.md` but not `workflow-no-memory.md`, and independent evaluation accepted both implementation artifacts plus all seven tests.

| Measure | Cell 14 | Per-cell ceiling |
| --- | ---: | ---: |
| Verified completion | 100% | required |
| Regressions | 0 | 0 |
| False completion | 0 | 0 |
| Estimated credits | 0.196740 | 0.5 |
| Wall time | 56.328 s | 300 s |
| Human interventions | 0 | 0 |

The measured turn used 97,056 input tokens, including 75,520 cached, 1,710 output tokens, and 342 reasoning tokens.

## Memory and trajectory

The workspace memory ledger exactly matched the source SHA-256 digest `e25068f66c1a0d5caf5fe2e6e8e894f5e5d43b62bd170f32908538c39fb02108`. Its deterministic view retrieved `restock-evidence`, `restock-current`, and `restock-failure`, excluded the superseded `restock-obsolete` entry, and evicted nothing. The agent explicitly recognized the reporting-only decision as obsolete, checked its evidence, and followed the current inventory/reporting split.

The privacy-safe trajectory contains seven events covering memory-aware inspection, baseline reproduction, a two-file patch, validation, the executor claim, and a passing independent audit. The observe-only watchdog emitted zero signals and made no intervention. Review found no memory-attributable error.

## Second supersession pair

| Measure | Control seed 1 | Treatment seed 1 | Treatment difference |
| --- | ---: | ---: | ---: |
| Verified completion | 1 / 1 | 1 / 1 | 0 |
| Regressions | 0 | 0 | 0 |
| Credits | 0.266027 | 0.196740 | -0.069287 (-26.05%) |
| Seconds | 85.140 | 56.328 | -28.812 (-33.84%) |

Across the first two restock seeds, both arms have equal verified completion and zero regressions. Treatments used `0.488895` credits versus `0.479737` for controls, a `1.91%` increase, while taking `124.390` seconds versus `150.281`, a `17.23%` reduction. The opposite cost direction between seeds demonstrates run-to-run variability; seed `2` is needed before interpreting the supersession block.

## Campaign state

The launcher paused after exactly one additional cell, as required:

- completed: `14 / 18`;
- measured cost so far: `3.058000 / 9.0` credits;
- measured model time so far: `916.828 / 5,400` seconds;
- human interventions: `0`;
- next declared cell: bounded phase-memory treatment, `restock-report`, seed `2`.

No later cell is authorized by this result. The next invocation requires a new explicit approval naming its task, seed, workflow arm, authenticated service, and `0.5`-credit/`300`-second ceilings.

## Evidence fingerprints

- Evaluation report: `fe198d55cb0b09f63327da77343e2498403d9e2ecb6c51b113e563e74988789a`
- Memory view: `c0b4912053392dd5b71eccd61766bc1237d16138b7a0f5369f51562bff2c97ac`
- Trajectory: `ac4231ffe26b8c48fba3c4becc0e7538f67b2a0d66fe3ce238b613b9cb0b5db7`
- Watchdog report: `dfca62c7a68d9536becca558e0ed1058781ae42c0dca49fedc4a51dea97ac93b`
- Campaign plan: `6367dd78e47b2880239bb4b143484c3a028f5e5e151e7bbb528f4e1c4e43076f`
- Live configuration: `1f5ce84cb123d9a9f3d8764de3028fe566d3f943b58f3f3f0321ed31e3e2d5a3`
- Execution inputs: `1c461c40d8e35ee222851d080ed6217e8ad36940916d0a171876db85446d5307`
