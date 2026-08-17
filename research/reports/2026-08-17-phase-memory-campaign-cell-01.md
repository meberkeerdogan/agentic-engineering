# Phase-Memory Campaign: Cell 01

**Date:** 2026-08-17

**Model:** `gpt-5.6-luna` through the existing ChatGPT Codex login

**Batch:** `codex-memory-campaign-001`

**Cell:** Canonical-rereading control, `median-fix`, seed `0`

## Result

The first campaign cell passed. A fresh plugin-free and MCP-free preflight succeeded, the task ran in an isolated workspace containing `workflow-no-memory.md` but not `workflow-phase-memory.md`, and independent evaluation accepted the median tests and calculator artifact with no regression or false completion.

| Measure | Cell 01 | Per-cell ceiling |
| --- | ---: | ---: |
| Verified completion | 100% | required |
| Regressions | 0 | 0 |
| False completion | 0 | 0 |
| Estimated credits | 0.179618 | 0.5 |
| Wall time | 59.063 s | 300 s |
| Human interventions | 0 | 0 |

The measured turn used 103,132 input tokens, including 83,456 cached, and 1,317 output tokens.

## Isolation and trajectory

The immutable memory ledger in the control workspace exactly matched the source SHA-256 digest `66e82a68394a5263913dd6d049dc882e75138578bd943d1938979fed8b032e91`. The treatment workflow was absent.

The privacy-safe trajectory contains navigation, explicit reproduction, one-file patching, validation, diff inspection, the executor claim, and a passing independent audit. The observe-only watchdog emitted zero signals and made no intervention.

## Campaign state

The launcher paused after exactly one cell, as required:

- completed: `1 / 18`;
- measured cost so far: `0.179618 / 9.0` credits;
- measured model time so far: `59.063 / 5,400` seconds;
- human interventions: `0`;
- next declared cell: canonical-rereading control, `median-fix`, seed `1`.

No later cell is authorized by this result. The next invocation requires a new explicit approval naming its task, seed, workflow arm, authenticated service, and `0.5`-credit/`300`-second ceilings.

## Evidence fingerprints

- Evaluation report: `34d1870900aeed91c76c93cc5ca9ef04fbd5835eae1a7a5124705d4f25bb3935`
- Trajectory: `705af8393da00df1bd4514e8eacbffc74e7eac80c53eda4faf1cb191292a29ba`
- Watchdog report: `6d203b175c514af2cf85eaee9d096632cca6c15b9048739515ff9d1c1270906b`
- Campaign plan: `6367dd78e47b2880239bb4b143484c3a028f5e5e151e7bbb528f4e1c4e43076f`
- Live configuration: `1f5ce84cb123d9a9f3d8764de3028fe566d3f943b58f3f3f0321ed31e3e2d5a3`
- Execution inputs: `1c461c40d8e35ee222851d080ed6217e8ad36940916d0a171876db85446d5307`
