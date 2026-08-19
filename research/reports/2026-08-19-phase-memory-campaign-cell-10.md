# Phase-Memory Campaign: Cell 10

**Date:** 2026-08-19

**Model:** `gpt-5.6-luna` through the existing ChatGPT Codex login

**Batch:** `codex-memory-campaign-001`

**Cell:** Bounded phase-memory treatment, `median-fix`, seed `0`

## Result

The tenth campaign cell passed and started the treatment half. A fresh plugin-free and MCP-free preflight succeeded, the task ran in an isolated workspace containing `workflow-phase-memory.md` but not `workflow-no-memory.md`, and independent evaluation accepted the calculator artifact plus all four median tests.

| Measure | Cell 10 | Per-cell ceiling |
| --- | ---: | ---: |
| Verified completion | 100% | required |
| Regressions | 0 | 0 |
| False completion | 0 | 0 |
| Estimated credits | 0.191772 | 0.5 |
| Wall time | 57.297 s | 300 s |
| Human interventions | 0 | 0 |

The measured turn used 111,852 input tokens, including 90,624 cached, and 1,344 output tokens.

## Memory and trajectory

The immutable memory ledger exactly matched the source SHA-256 digest `66e82a68394a5263913dd6d049dc882e75138578bd943d1938979fed8b032e91`. A deterministic local rebuild matched the predeclared memory-view fingerprint `88a62fe80b0eebdfd04d287df62cf37ee89aa7cea28889333bfe9e38ecd0548b` and retrieved `median-decision` and `median-failure`, with no superseded or evicted entries. The agent read the treatment workflow and ledger, checked the remembered summaries against the canonical specification, tests, and implementation, and did not modify the ledger.

The privacy-safe trajectory contains eight events covering memory-aware inspection, baseline reproduction, a one-file patch, validation, final diff inspection, the executor claim, and a passing independent audit. The observe-only watchdog emitted zero signals and made no intervention. Review found no memory-attributable error.

## First paired comparison

| Measure | Control seed 0 | Treatment seed 0 | Treatment difference |
| --- | ---: | ---: | ---: |
| Verified completion | 100% | 100% | 0 points |
| Regressions | 0 | 0 | 0 |
| Credits | 0.179618 | 0.191772 | +0.012154 (+6.77%) |
| Seconds | 59.063 | 57.297 | -1.766 (-2.99%) |

This low-pressure negative-control pair shows equal task quality with a small cost increase and time decrease for treatment. One pair cannot establish whether phase memory changes efficiency, and this simple task was not expected to need memory pressure relief.

## Campaign state

The launcher paused after exactly one additional cell, as required:

- completed: `10 / 18`;
- measured cost so far: `2.124129 / 9.0` credits;
- measured model time so far: `676.548 / 5,400` seconds;
- human interventions: `0`;
- next declared cell: bounded phase-memory treatment, `median-fix`, seed `1`.

No later cell is authorized by this result. The next invocation requires a new explicit approval naming its task, seed, workflow arm, authenticated service, and `0.5`-credit/`300`-second ceilings.

## Evidence fingerprints

- Evaluation report: `34d1870900aeed91c76c93cc5ca9ef04fbd5835eae1a7a5124705d4f25bb3935`
- Memory view: `88a62fe80b0eebdfd04d287df62cf37ee89aa7cea28889333bfe9e38ecd0548b`
- Trajectory: `ebe0248862a16a9a2b0eb6a40d38ff68df50d4081014f0a9090fa0906b355204`
- Watchdog report: `1ebc1fbc4c8cc2e402ff21d0b8a515cdc778db9c336482be4fcdd5d1ef44937c`
- Campaign plan: `6367dd78e47b2880239bb4b143484c3a028f5e5e151e7bbb528f4e1c4e43076f`
- Live configuration: `1f5ce84cb123d9a9f3d8764de3028fe566d3f943b58f3f3f0321ed31e3e2d5a3`
- Execution inputs: `1c461c40d8e35ee222851d080ed6217e8ad36940916d0a171876db85446d5307`
