# Phase-Memory Live Sentinel: Control

**Date:** 2026-08-17

**Model:** `gpt-5.6-luna` through the existing ChatGPT Codex login

**Batch:** `codex-memory-sentinel-001`

**Scope:** The canonical-rereading control cell for one eviction-pressure roadmap evolution task and one seed. The bounded phase-memory treatment was not authorized or run.

## Result

The control passed its safety gate. A fresh plugin-free and MCP-free preflight succeeded, the task ran in an isolated workspace containing `workflow-no-memory.md` but not `workflow-phase-memory.md`, and independent evaluation accepted every required feature, protected test, and artifact check.

| Measure | Control | Hard ceiling |
| --- | ---: | ---: |
| Verified completion | 100% | required |
| Regressions | 0 | 0 |
| False completion | 0 | 0 |
| Estimated credits | 0.227309 | 0.75 |
| Wall time | 79.625 s | 450 s |
| Human interventions | 0 | 0 |

The measured turn used 114,553 input tokens, including 91,648 cached, and 2,232 output tokens. The rate card dated 2026-08-16 converted this usage to `0.227309` credits.

The source repository remained clean. Private raw output stays in ignored `.agentic-runs/live-batches/codex-memory-sentinel-001/` storage.

## Isolation and memory integrity

The isolated workspace retained the shared immutable `phase-memory.json` ledger and only the selected canonical-rereading workflow. The ledger SHA-256 digest, `bfd76819f32a2711aa824afbd02c0def77621956f093690ae67c0777f17bea79`, exactly matched the source fixture. The agent changed only the task implementation files evaluated by the contract.

## Trajectory review

The privacy-safe trajectory contains eight events: navigation, explicit reproduction, a two-file patch, validation, diff inspection, the executor claim, and a passing independent audit. The observe-only watchdog emitted zero signals and made no intervention. Review found no reliance on superseded, evicted, unrelated, or unevidenced memory.

## Decision

The canonical-rereading control satisfies the sentinel's technical and budget gates. It does not establish that bounded phase memory is useful. The treatment remains pending and requires a new explicit approval for the authenticated Codex service with the same `0.75`-credit and `450`-second ceilings.

## Evidence fingerprints

- Evaluation report: `ef27a07d9a108f78a3d678ae57d34179f6e20b6c51a01551a68244d44970aa86`
- Trajectory: `72efa1237b6f918afc37e99dcb856e68210fd8801cce7bdf80e079ce7cae6d79`
- Watchdog report: `ca5651df63f32bc9cf2ed55fad8d55109f97cf8e572f3ab8117a85555b40dafe`
- Batch plan: `86f133f250b1bcfc494147f42c1ed432337f814034bc2095306620c025695d42`
- Live configuration: `8d3d37701f9ef3bc5c7e166a64121a408d3fecdec023cb9c0c712073ad143791`
- Execution inputs: `23c09c7d9128f1a0e77b7f79f91bd10e83d9504e463bf3f9d423251311050404`
