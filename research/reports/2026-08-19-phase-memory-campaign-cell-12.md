# Phase-Memory Campaign: Cell 12

**Date:** 2026-08-19

**Model:** `gpt-5.6-luna` through the existing ChatGPT Codex login

**Batch:** `codex-memory-campaign-001`

**Cell:** Bounded phase-memory treatment, `median-fix`, seed `2`

## Result

The twelfth campaign cell passed and completed the three-seed low-pressure treatment block. A fresh plugin-free and MCP-free preflight succeeded, the task ran in an isolated workspace containing `workflow-phase-memory.md` but not `workflow-no-memory.md`, and independent evaluation accepted the calculator artifact plus all four median tests.

| Measure | Cell 12 | Per-cell ceiling |
| --- | ---: | ---: |
| Verified completion | 100% | required |
| Regressions | 0 | 0 |
| False completion | 0 | 0 |
| Estimated credits | 0.260437 | 0.5 |
| Wall time | 61.250 s | 300 s |
| Human interventions | 0 | 0 |

The measured turn used 108,335 input tokens, including 71,424 cached, and 1,339 output tokens.

## Memory and trajectory

The immutable memory ledger exactly matched the source SHA-256 digest `66e82a68394a5263913dd6d049dc882e75138578bd943d1938979fed8b032e91`. Its predeclared deterministic view retrieves `median-decision` and `median-failure`, with no superseded or evicted entries. The agent read the treatment workflow, ledger, evidence contract, implementation, and tests before reproducing the failure and did not modify the ledger.

The privacy-safe trajectory contains eight events covering memory-aware inspection, baseline reproduction, a one-file patch, validation, final diff inspection, the executor claim, and a passing independent audit. The observe-only watchdog emitted zero signals and made no intervention. Review found no memory-attributable error.

## Median block comparison

| Measure | Three controls | Three treatments | Treatment difference |
| --- | ---: | ---: | ---: |
| Verified completion | 3 / 3 | 3 / 3 | 0 |
| Regressions | 0 | 0 | 0 |
| Total credits | 0.529814 | 0.636748 | +0.106934 (+20.18%) |
| Total seconds | 179.923 | 173.187 | -6.736 (-3.74%) |

For seed `2` alone, treatment cost `32.59%` more and finished `16.40%` faster than control, with equal quality. Across all three low-pressure pairs, bounded memory remained safe but added measured credit cost without improving verified completion. The treatment was slightly faster overall. This negative-control block does not test the intended supersession or eviction benefits.

## Campaign state

The launcher paused after exactly one additional cell, as required:

- completed: `12 / 18`;
- measured cost so far: `2.569105 / 9.0` credits;
- measured model time so far: `792.438 / 5,400` seconds;
- human interventions: `0`;
- next declared cell: bounded phase-memory treatment, `restock-report`, seed `0`.

No later cell is authorized by this result. The next invocation requires a new explicit approval naming its task, seed, workflow arm, authenticated service, and `0.5`-credit/`300`-second ceilings.

## Evidence fingerprints

- Evaluation report: `34d1870900aeed91c76c93cc5ca9ef04fbd5835eae1a7a5124705d4f25bb3935`
- Memory view: `88a62fe80b0eebdfd04d287df62cf37ee89aa7cea28889333bfe9e38ecd0548b`
- Trajectory: `6c016271e503ade8780610d358050ab2a5fcf571fe1b84476a629e57abd90516`
- Watchdog report: `d4a9aa5da8b62ddf9fcb3a04d3fe637d6c8a0ecf039e48bab0e94d4df66bce8a`
- Campaign plan: `6367dd78e47b2880239bb4b143484c3a028f5e5e151e7bbb528f4e1c4e43076f`
- Live configuration: `1f5ce84cb123d9a9f3d8764de3028fe566d3f943b58f3f3f0321ed31e3e2d5a3`
- Execution inputs: `1c461c40d8e35ee222851d080ed6217e8ad36940916d0a171876db85446d5307`
