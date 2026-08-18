# Phase-Memory Campaign: Cell 04

**Date:** 2026-08-18

**Model:** `gpt-5.6-luna` through the existing ChatGPT Codex login

**Batch:** `codex-memory-campaign-001`

**Cell:** Canonical-rereading control, `restock-report`, seed `0`

## Result

The fourth campaign cell passed and started the supersession-pressure control block. A fresh plugin-free and MCP-free preflight succeeded, the task ran in an isolated workspace containing `workflow-no-memory.md` but not `workflow-phase-memory.md`, and independent evaluation accepted both required files plus all seven existing and restock tests.

| Measure | Cell 04 | Per-cell ceiling |
| --- | ---: | ---: |
| Verified completion | 100% | required |
| Regressions | 0 | 0 |
| False completion | 0 | 0 |
| Estimated credits | 0.213710 | 0.5 |
| Wall time | 65.141 s | 300 s |
| Human interventions | 0 | 0 |

The measured turn used 125,314 input tokens, including 103,680 cached, and 1,790 output tokens.

## Isolation and trajectory

The immutable memory ledger in the control workspace exactly matched the task source SHA-256 digest `e25068f66c1a0d5caf5fe2e6e8e894f5e5d43b62bd170f32908538c39fb02108`. The treatment workflow was absent.

The privacy-safe trajectory contains nine events covering inspection, baseline reproduction, the two-file patch, validation, the executor claim, and a passing independent audit. The observe-only watchdog emitted one `stagnation` signal because four normal inspection and reproduction events did not change repository state. Manual trajectory review classified this as a contextual false positive: the agent was gathering evidence before editing. The watchdog made no intervention.

## Campaign state

The launcher paused after exactly one additional cell, as required:

- completed: `4 / 18`;
- measured cost so far: `0.743524 / 9.0` credits;
- measured model time so far: `245.064 / 5,400` seconds;
- human interventions: `0`;
- next declared cell: canonical-rereading control, `restock-report`, seed `1`.

This first restock control run establishes a valid baseline under supersession pressure. It does not yet compare canonical rereading with bounded phase memory.

No later cell is authorized by this result. The next invocation requires a new explicit approval naming its task, seed, workflow arm, authenticated service, and `0.5`-credit/`300`-second ceilings.

## Evidence fingerprints

- Evaluation report: `c604f9e6536ad8724258fc13437b3322ba0134d053fd417197361e275dec5a2b`
- Trajectory: `280f70d4222982e1d489435fe6ed5b6411671befed592604a5034ccb2082d91e`
- Watchdog report: `96bc1423733b7007c673c3b547cf54c2a3c0cc73982b6087fad71af51aafdac7`
- Campaign plan: `6367dd78e47b2880239bb4b143484c3a028f5e5e151e7bbb528f4e1c4e43076f`
- Live configuration: `1f5ce84cb123d9a9f3d8764de3028fe566d3f943b58f3f3f0321ed31e3e2d5a3`
- Execution inputs: `1c461c40d8e35ee222851d080ed6217e8ad36940916d0a171876db85446d5307`
