# Phase-Memory Campaign: Cell 11

**Date:** 2026-08-19

**Model:** `gpt-5.6-luna` through the existing ChatGPT Codex login

**Batch:** `codex-memory-campaign-001`

**Cell:** Bounded phase-memory treatment, `median-fix`, seed `1`

## Result

The eleventh campaign cell passed. A fresh plugin-free and MCP-free preflight succeeded, the task ran in an isolated workspace containing `workflow-phase-memory.md` but not `workflow-no-memory.md`, and independent evaluation accepted the calculator artifact plus all four median tests.

| Measure | Cell 11 | Per-cell ceiling |
| --- | ---: | ---: |
| Verified completion | 100% | required |
| Regressions | 0 | 0 |
| False completion | 0 | 0 |
| Estimated credits | 0.184539 | 0.5 |
| Wall time | 54.640 s | 300 s |
| Human interventions | 0 | 0 |

The measured turn used 107,511 input tokens, including 86,528 cached, and 1,212 output tokens.

## Memory and trajectory

The immutable memory ledger exactly matched the source SHA-256 digest `66e82a68394a5263913dd6d049dc882e75138578bd943d1938979fed8b032e91`. Its predeclared deterministic view retrieves `median-decision` and `median-failure`, with no superseded or evicted entries. The agent read the treatment workflow, ledger, evidence contract, implementation, and tests before reproducing the failure and did not modify the ledger.

The privacy-safe trajectory contains eight events covering memory-aware inspection, baseline reproduction, a one-file patch, validation, final diff inspection, the executor claim, and a passing independent audit. The observe-only watchdog emitted zero signals and made no intervention. Review found no memory-attributable error.

## Paired comparison

| Measure | Control seed 1 | Treatment seed 1 | Treatment difference |
| --- | ---: | ---: | ---: |
| Verified completion | 100% | 100% | 0 points |
| Regressions | 0 | 0 | 0 |
| Credits | 0.153771 | 0.184539 | +0.030768 (+20.01%) |
| Seconds | 47.594 | 54.640 | +7.046 (+14.80%) |

Across the first two median pairs, both workflows are `2 / 2` verified with zero regressions. Treatment has used `12.87%` more credits and `4.95%` more time in total. The third seed is still required, and this low-pressure task is a negative control rather than the target use case for memory.

## Campaign state

The launcher paused after exactly one additional cell, as required:

- completed: `11 / 18`;
- measured cost so far: `2.308668 / 9.0` credits;
- measured model time so far: `731.188 / 5,400` seconds;
- human interventions: `0`;
- next declared cell: bounded phase-memory treatment, `median-fix`, seed `2`.

No later cell is authorized by this result. The next invocation requires a new explicit approval naming its task, seed, workflow arm, authenticated service, and `0.5`-credit/`300`-second ceilings.

## Evidence fingerprints

- Evaluation report: `34d1870900aeed91c76c93cc5ca9ef04fbd5835eae1a7a5124705d4f25bb3935`
- Memory view: `88a62fe80b0eebdfd04d287df62cf37ee89aa7cea28889333bfe9e38ecd0548b`
- Trajectory: `aa0994728c8dd17d7288d03dcb8636e34f282f4fc71285199d118b3f71452440`
- Watchdog report: `f9ed6e4c7d403b3d081aa12bc3d8ed5d61c44f9ac1501c40323f67d78ee9ce1f`
- Campaign plan: `6367dd78e47b2880239bb4b143484c3a028f5e5e151e7bbb528f4e1c4e43076f`
- Live configuration: `1f5ce84cb123d9a9f3d8764de3028fe566d3f943b58f3f3f0321ed31e3e2d5a3`
- Execution inputs: `1c461c40d8e35ee222851d080ed6217e8ad36940916d0a171876db85446d5307`
