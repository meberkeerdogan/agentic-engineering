# Phase-Memory Campaign: Cell 05

**Date:** 2026-08-18

**Model:** `gpt-5.6-luna` through the existing ChatGPT Codex login

**Batch:** `codex-memory-campaign-001`

**Cell:** Canonical-rereading control, `restock-report`, seed `1`

## Result

The fifth campaign cell passed. A fresh plugin-free and MCP-free preflight succeeded, the task ran in an isolated workspace containing `workflow-no-memory.md` but not `workflow-phase-memory.md`, and independent evaluation accepted both required files plus all seven existing and restock tests.

| Measure | Cell 05 | Per-cell ceiling |
| --- | ---: | ---: |
| Verified completion | 100% | required |
| Regressions | 0 | 0 |
| False completion | 0 | 0 |
| Estimated credits | 0.266027 | 0.5 |
| Wall time | 85.140 s | 300 s |
| Human interventions | 0 | 0 |

The measured turn used 148,291 input tokens, including 123,904 cached, and 2,738 output tokens.

## Isolation and trajectory

The immutable memory ledger in the control workspace exactly matched the task source SHA-256 digest `e25068f66c1a0d5caf5fe2e6e8e894f5e5d43b62bd170f32908538c39fb02108`. The treatment workflow was absent.

The privacy-safe trajectory contains eight events: repository inspection, baseline reproduction, a two-file patch, validation, final diff inspection, the executor claim, and a passing independent audit. The observe-only watchdog emitted zero signals and made no intervention. Compared with seed `0`, this run performed one fewer unchanged pre-edit action, so it did not cross the watchdog's stagnation threshold.

## Campaign state

The launcher paused after exactly one additional cell, as required:

- completed: `5 / 18`;
- measured cost so far: `1.009551 / 9.0` credits;
- measured model time so far: `330.204 / 5,400` seconds;
- human interventions: `0`;
- next declared cell: canonical-rereading control, `restock-report`, seed `2`.

Two restock control seeds have now independently verified. This is useful baseline evidence under supersession pressure, but it still does not compare canonical rereading with bounded phase memory.

No later cell is authorized by this result. The next invocation requires a new explicit approval naming its task, seed, workflow arm, authenticated service, and `0.5`-credit/`300`-second ceilings.

## Evidence fingerprints

- Evaluation report: `a5dadf5416702cd942567e41e6c3ecd3179fa00e1e9e1eb0602dbb16d7e42bee`
- Trajectory: `9ae262691427603aa6aa9f882edbb29e61ec4a5ec639fbc35bafb70ff9168c5a`
- Watchdog report: `9dc19bfc70db4e5be518806d4878a5a05da26d611628e331e06bd41dee0b427a`
- Campaign plan: `6367dd78e47b2880239bb4b143484c3a028f5e5e151e7bbb528f4e1c4e43076f`
- Live configuration: `1f5ce84cb123d9a9f3d8764de3028fe566d3f943b58f3f3f0321ed31e3e2d5a3`
- Execution inputs: `1c461c40d8e35ee222851d080ed6217e8ad36940916d0a171876db85446d5307`
