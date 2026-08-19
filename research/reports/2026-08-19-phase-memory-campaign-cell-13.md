# Phase-Memory Campaign: Cell 13

**Date:** 2026-08-19

**Model:** `gpt-5.6-luna` through the existing ChatGPT Codex login

**Batch:** `codex-memory-campaign-001`

**Cell:** Bounded phase-memory treatment, `restock-report`, seed `0`

## Result

The thirteenth campaign cell passed and started the supersession-pressure treatment block. A fresh plugin-free and MCP-free preflight succeeded, the task ran in an isolated workspace containing `workflow-phase-memory.md` but not `workflow-no-memory.md`, and independent evaluation accepted both implementation artifacts plus all seven tests.

| Measure | Cell 13 | Per-cell ceiling |
| --- | ---: | ---: |
| Verified completion | 100% | required |
| Regressions | 0 | 0 |
| False completion | 0 | 0 |
| Estimated credits | 0.292155 | 0.5 |
| Wall time | 68.062 s | 300 s |
| Human interventions | 0 | 0 |

The measured turn used 133,191 input tokens, including 94,720 cached, 1,748 output tokens, and 277 reasoning tokens.

## Memory and trajectory

The workspace memory ledger exactly matched the source SHA-256 digest `e25068f66c1a0d5caf5fe2e6e8e894f5e5d43b62bd170f32908538c39fb02108`. Its deterministic view retrieved `restock-evidence`, `restock-current`, and `restock-failure`, excluded the superseded `restock-obsolete` entry, and evicted nothing. The agent explicitly identified the reporting-only normalization idea as obsolete and followed the current split: selection and validation in `inventory.py`, formatting in `reporting.py`.

The privacy-safe trajectory contains nine events covering memory-aware inspection, baseline reproduction, a two-file patch, validation, final diff inspection, the executor claim, and a passing independent audit. The observe-only watchdog emitted one stagnation candidate because validation and diff inspection correctly left the patched state unchanged. This was a contextual false positive and made no intervention. Review found no memory-attributable error.

## First supersession pair

| Measure | Control seed 0 | Treatment seed 0 | Treatment difference |
| --- | ---: | ---: | ---: |
| Verified completion | 1 / 1 | 1 / 1 | 0 |
| Regressions | 0 | 0 | 0 |
| Credits | 0.213710 | 0.292155 | +0.078445 (+36.71%) |
| Seconds | 65.141 | 68.062 | +2.921 (+4.48%) |

The treatment handled supersession correctly, but the canonical-rereading control also completed successfully. This first pair therefore shows correct memory behavior, not a completion benefit. It also shows higher measured cost and time; the remaining two restock seeds are needed before interpreting the block.

## Campaign state

The launcher paused after exactly one additional cell, as required:

- completed: `13 / 18`;
- measured cost so far: `2.861260 / 9.0` credits;
- measured model time so far: `860.500 / 5,400` seconds;
- human interventions: `0`;
- next declared cell: bounded phase-memory treatment, `restock-report`, seed `1`.

No later cell is authorized by this result. The next invocation requires a new explicit approval naming its task, seed, workflow arm, authenticated service, and `0.5`-credit/`300`-second ceilings.

## Evidence fingerprints

- Evaluation report: `9706d5d1f46a77c2e42c05bf6815bae3d633ba2fbbb65d178807ec30c18c4e67`
- Memory view: `c0b4912053392dd5b71eccd61766bc1237d16138b7a0f5369f51562bff2c97ac`
- Trajectory: `25bb268e6c11ade733364ca7a008abebf06148180d2f92753efb7c22bd5cb1dd`
- Watchdog report: `baba5f63bfb3189fb9995cf8accb55964fb4c81f4490c417b4e8c73b65b5b24f`
- Campaign plan: `6367dd78e47b2880239bb4b143484c3a028f5e5e151e7bbb528f4e1c4e43076f`
- Live configuration: `1f5ce84cb123d9a9f3d8764de3028fe566d3f943b58f3f3f0321ed31e3e2d5a3`
- Execution inputs: `1c461c40d8e35ee222851d080ed6217e8ad36940916d0a171876db85446d5307`
