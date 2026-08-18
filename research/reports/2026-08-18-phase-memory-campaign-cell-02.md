# Phase-Memory Campaign: Cell 02

**Date:** 2026-08-18

**Model:** `gpt-5.6-luna` through the existing ChatGPT Codex login

**Batch:** `codex-memory-campaign-001`

**Cell:** Canonical-rereading control, `median-fix`, seed `1`

## Result

The second campaign cell passed. A fresh plugin-free and MCP-free preflight succeeded, the task ran in an isolated workspace containing `workflow-no-memory.md` but not `workflow-phase-memory.md`, and independent evaluation accepted the median tests and calculator artifact with no regression or false completion.

| Measure | Cell 02 | Per-cell ceiling |
| --- | ---: | ---: |
| Verified completion | 100% | required |
| Regressions | 0 | 0 |
| False completion | 0 | 0 |
| Estimated credits | 0.153771 | 0.5 |
| Wall time | 47.594 s | 300 s |
| Human interventions | 0 | 0 |

The measured turn used 86,421 input tokens, including 68,352 cached, and 975 output tokens.

## Isolation and trajectory

The immutable memory ledger in the control workspace exactly matched the campaign's `examples/live-pilot-template/phase-memory.json` SHA-256 digest `66e82a68394a5263913dd6d049dc882e75138578bd943d1938979fed8b032e91`. The treatment workflow was absent.

The privacy-safe trajectory contains seven events: navigation, baseline diff inspection, explicit reproduction, one-file patching, validation, the executor claim, and a passing independent audit. The observe-only watchdog emitted zero signals and made no intervention.

## Campaign state

The launcher paused after exactly one additional cell, as required:

- completed: `2 / 18`;
- measured cost so far: `0.333389 / 9.0` credits;
- measured model time so far: `106.657 / 5,400` seconds;
- human interventions: `0`;
- next declared cell: canonical-rereading control, `median-fix`, seed `2`.

No later cell is authorized by this result. The next invocation requires a new explicit approval naming its task, seed, workflow arm, authenticated service, and `0.5`-credit/`300`-second ceilings.

## Evidence fingerprints

- Evaluation report: `e79b39a694f0f350664c43ee8ce148bb4c2619805eaeebb488d7025142e14140`
- Trajectory: `db9bd1b9aad6720424cc9cffbb3e1b77a962d197961c77b8c044d7a030f16640`
- Watchdog report: `63c555e114e8374f56d61958e9939fba3758228a5265f8cc9e3d4f3aa2584e6e`
- Campaign plan: `6367dd78e47b2880239bb4b143484c3a028f5e5e151e7bbb528f4e1c4e43076f`
- Live configuration: `1f5ce84cb123d9a9f3d8764de3028fe566d3f943b58f3f3f0321ed31e3e2d5a3`
- Execution inputs: `1c461c40d8e35ee222851d080ed6217e8ad36940916d0a171876db85446d5307`
