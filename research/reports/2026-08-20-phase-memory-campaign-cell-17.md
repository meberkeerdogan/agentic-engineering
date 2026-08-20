# Phase-Memory Campaign: Cell 17

**Date:** 2026-08-20

**Model:** `gpt-5.6-luna` through the existing ChatGPT Codex login

**Batch:** `codex-memory-campaign-001`

**Cell:** Bounded phase-memory treatment, `roadmap-evolution`, seed `1`

## Result

The seventeenth campaign cell passed. A fresh plugin-free and MCP-free preflight succeeded, the task ran in an isolated workspace containing `workflow-phase-memory.md` but not `workflow-no-memory.md`, and independent evaluation accepted both implementation artifacts plus all six tests.

| Measure | Cell 17 | Per-cell ceiling |
| --- | ---: | ---: |
| Verified completion | 100% | required |
| Regressions | 0 | 0 |
| False completion | 0 | 0 |
| Estimated credits | 0.233522 | 0.5 |
| Wall time | 66.140 s | 300 s |
| Human interventions | 0 | 0 |

The measured turn used 120,448 input tokens, including 95,744 cached, 2,071 output tokens, and 349 reasoning tokens.

## Memory and trajectory

The workspace memory ledger exactly matched the source SHA-256 digest `bfd76819f32a2711aa824afbd02c0def77621956f093690ae67c0777f17bea79`. Its deterministic view retained and retrieved `roadmap-current`, `roadmap-evidence`, and `roadmap-failure`, while capacity eviction removed the unrelated `roadmap-distractor`. The agent used the relevant entries, reproduced the expected baseline failure, and preserved protected behavior.

The privacy-safe trajectory contains eight events covering memory-aware inspection, baseline reproduction, a two-file patch, validation, final diff inspection, the executor claim, and a passing independent audit. The observe-only watchdog emitted zero signals and made no intervention. Review found no memory-attributable error.

## Second eviction pair

| Measure | Control seed 1 | Treatment seed 1 | Treatment difference |
| --- | ---: | ---: | ---: |
| Verified completion | 1 / 1 | 1 / 1 | 0 |
| Regressions | 0 | 0 | 0 |
| Credits | 0.202453 | 0.233522 | +0.031069 (+15.35%) |
| Seconds | 55.734 | 66.140 | +10.406 (+18.67%) |

Across the first two roadmap seeds, both arms have equal verified completion and zero regressions. Treatments used `0.451065` credits versus `0.452076` for controls, a `0.22%` reduction, while taking `133.249` seconds versus `135.484`, a `1.65%` reduction. Seed `0` favored treatment while seed `1` favored control, leaving the two-pair aggregate nearly equal. Seed `2` is required before interpreting the eviction block or the complete campaign.

## Campaign state

The launcher paused after exactly one additional cell, as required:

- completed: `17 / 18`;
- measured cost so far: `3.740817 / 9.0` credits;
- measured model time so far: `1,125.640 / 5,400` seconds;
- human interventions: `0`;
- next declared cell: bounded phase-memory treatment, `roadmap-evolution`, seed `2`.

No later cell is authorized by this result. The final invocation requires a new explicit approval naming its task, seed, workflow arm, authenticated service, and `0.5`-credit/`300`-second ceilings.

## Evidence fingerprints

- Evaluation report: `f049744f376f63d7f592e7506ad3739998d6c34cb44cefb7bd7166849c7778e8`
- Memory view: `22acaeeb9261e0aa466de960fbf7d1e0f6ad1985471100e4d297a90fdd459594`
- Trajectory: `004f681f6edf72cd7caf2b610058304f05606671477f7ce83c31ff5a28c47fa0`
- Watchdog report: `7fb38b26cb4ccda89be496e046fbb3b7fc9e933951f548b7279b34eacf73b322`
- Campaign plan: `6367dd78e47b2880239bb4b143484c3a028f5e5e151e7bbb528f4e1c4e43076f`
- Live configuration: `1f5ce84cb123d9a9f3d8764de3028fe566d3f943b58f3f3f0321ed31e3e2d5a3`
- Execution inputs: `1c461c40d8e35ee222851d080ed6217e8ad36940916d0a171876db85446d5307`
