# Phase-Memory Campaign: Cell 08

**Date:** 2026-08-19

**Model:** `gpt-5.6-luna` through the existing ChatGPT Codex login

**Batch:** `codex-memory-campaign-001`

**Cell:** Canonical-rereading control, `roadmap-evolution`, seed `1`

## Result

The eighth campaign cell passed. A fresh plugin-free and MCP-free preflight succeeded, the task ran in an isolated workspace containing `workflow-no-memory.md` but not `workflow-phase-memory.md`, and independent evaluation accepted both required files plus all six existing and roadmap-evolution tests.

| Measure | Cell 08 | Per-cell ceiling |
| --- | ---: | ---: |
| Verified completion | 100% | required |
| Regressions | 0 | 0 |
| False completion | 0 | 0 |
| Estimated credits | 0.202453 | 0.5 |
| Wall time | 55.734 s | 300 s |
| Human interventions | 0 | 0 |

The measured turn used 97,691 input tokens, including 74,496 cached, and 1,641 output tokens.

## Isolation and trajectory

The immutable memory ledger in the control workspace exactly matched the task source SHA-256 digest `bfd76819f32a2711aa824afbd02c0def77621956f093690ae67c0777f17bea79`. The treatment workflow was absent.

The privacy-safe trajectory contains seven events: repository inspection, baseline reproduction, a two-file patch, validation, the executor claim, and a passing independent audit. The observe-only watchdog emitted zero signals and made no intervention. This run used two fewer recorded events than seed `0` and was cheaper and faster, but two observations cannot establish that trajectory length caused the difference.

## Campaign state

The launcher paused after exactly one additional cell, as required:

- completed: `8 / 18`;
- measured cost so far: `1.701510 / 9.0` credits;
- measured model time so far: `540.985 / 5,400` seconds;
- human interventions: `0`;
- next declared cell: canonical-rereading control, `roadmap-evolution`, seed `2`.

Two roadmap control seeds have now independently verified. This remains baseline evidence only; the bounded-memory treatment has not yet run in this campaign.

No later cell is authorized by this result. The next invocation requires a new explicit approval naming its task, seed, workflow arm, authenticated service, and `0.5`-credit/`300`-second ceilings.

## Evidence fingerprints

- Evaluation report: `8bd4e02fcf9113055d684d4309c3cc1d246423f5eae8d031110ed259a0f4e419`
- Trajectory: `1cafaa511f0b051e334722f791a01076f18f4a92a2c608b477ef72fa350ceb14`
- Watchdog report: `81890939f818fed366822cf62b4f5ead7872e382daed50747e11aa465ef7fd74`
- Campaign plan: `6367dd78e47b2880239bb4b143484c3a028f5e5e151e7bbb528f4e1c4e43076f`
- Live configuration: `1f5ce84cb123d9a9f3d8764de3028fe566d3f943b58f3f3f0321ed31e3e2d5a3`
- Execution inputs: `1c461c40d8e35ee222851d080ed6217e8ad36940916d0a171876db85446d5307`
