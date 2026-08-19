# Phase-Memory Campaign: Cell 15

**Date:** 2026-08-19

**Model:** `gpt-5.6-luna` through the existing ChatGPT Codex login

**Batch:** `codex-memory-campaign-001`

**Cell:** Bounded phase-memory treatment, `restock-report`, seed `2`

## Result

The fifteenth campaign cell passed and completed the three-seed supersession-pressure block. A fresh plugin-free and MCP-free preflight succeeded, the task ran in an isolated workspace containing `workflow-phase-memory.md` but not `workflow-no-memory.md`, and independent evaluation accepted both implementation artifacts plus all seven tests.

| Measure | Cell 15 | Per-cell ceiling |
| --- | ---: | ---: |
| Verified completion | 100% | required |
| Regressions | 0 | 0 |
| False completion | 0 | 0 |
| Estimated credits | 0.231752 | 0.5 |
| Wall time | 75.563 s | 300 s |
| Human interventions | 0 | 0 |

The measured turn used 133,624 input tokens, including 109,824 cached, 1,928 output tokens, and 328 reasoning tokens.

## Memory and trajectory

The workspace memory ledger exactly matched the source SHA-256 digest `e25068f66c1a0d5caf5fe2e6e8e894f5e5d43b62bd170f32908538c39fb02108`. Its deterministic view retrieved `restock-evidence`, `restock-current`, and `restock-failure`, excluded the superseded `restock-obsolete` entry, and evicted nothing. The agent checked the workflow, ledger, evidence contract, source, and tests, then followed the current inventory/reporting split rather than the obsolete reporting-only choice.

The privacy-safe trajectory contains nine events covering memory-aware inspection, baseline reproduction, a two-file patch, validation, final diff inspection, the executor claim, and a passing independent audit. The observe-only watchdog emitted one stagnation candidate because repeated validation and diff inspection correctly left the patched state unchanged. This was a contextual false positive and made no intervention. Review found no memory-attributable error.

## Complete supersession block

| Measure | Three controls | Three treatments | Treatment difference |
| --- | ---: | ---: | ---: |
| Verified completion | 3 / 3 | 3 / 3 | 0 |
| Regressions | 0 | 0 | 0 |
| Total credits | 0.719620 | 0.720647 | +0.001027 (+0.14%) |
| Total seconds | 225.578 | 199.953 | -25.625 (-11.36%) |

For seed `2` alone, treatment cost `3.39%` less and took `0.35%` longer than control, with equal quality. Across all three restock pairs, bounded memory reliably removed the obsolete instruction and was faster overall at essentially equal measured cost. It did not improve verified completion because every control also succeeded. This supports correct and safe supersession behavior, but it does not satisfy the predeclared requirement for a completion improvement on memory-pressure tasks.

## Campaign state

The launcher paused after exactly one additional cell, as required:

- completed: `15 / 18`;
- measured cost so far: `3.289752 / 9.0` credits;
- measured model time so far: `992.391 / 5,400` seconds;
- human interventions: `0`;
- next declared cell: bounded phase-memory treatment, `roadmap-evolution`, seed `0`.

No later cell is authorized by this result. The next invocation requires a new explicit approval naming its task, seed, workflow arm, authenticated service, and `0.5`-credit/`300`-second ceilings.

## Evidence fingerprints

- Evaluation report: `ed79c5c48ca068d907fb412abd1b4bedcac7de7d9485ca6b6eb556775f167468`
- Memory view: `c0b4912053392dd5b71eccd61766bc1237d16138b7a0f5369f51562bff2c97ac`
- Trajectory: `ecb36055974647f435df4ccaf8d80a3edcd17044825933c478b05188c12a3f63`
- Watchdog report: `d06553c57feae44f4c0e3d077233e91c44c7ce70b55a25449c23b604cb138148`
- Campaign plan: `6367dd78e47b2880239bb4b143484c3a028f5e5e151e7bbb528f4e1c4e43076f`
- Live configuration: `1f5ce84cb123d9a9f3d8764de3028fe566d3f943b58f3f3f0321ed31e3e2d5a3`
- Execution inputs: `1c461c40d8e35ee222851d080ed6217e8ad36940916d0a171876db85446d5307`
