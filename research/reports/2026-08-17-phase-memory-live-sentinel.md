# Phase-Memory Live Sentinel

**Date:** 2026-08-17

**Model:** `gpt-5.6-luna` through the existing ChatGPT Codex login

**Batch:** `codex-memory-sentinel-001`

**Scope:** One eviction-pressure roadmap evolution task, one seed, one canonical-rereading control, and one bounded phase-memory treatment

## Result

The phase-memory sentinel passed its safety gate. Both arms ran in isolated plugin-free and MCP-free environments, retained the same immutable memory ledger, and contained only their selected memory workflow. Independent evaluation accepted every required feature, protected test, and artifact check with no regressions, false completion, or human intervention.

| Measure | Canonical rereading | Bounded memory | Treatment delta |
| --- | ---: | ---: | ---: |
| Verified completion | 100% | 100% | 0 |
| Regressions | 0 | 0 | 0 |
| False completion | 0 | 0 | 0 |
| Estimated credits | 0.227309 | 0.219144 | -0.008165 (-3.59%) |
| Wall time | 79.625 s | 72.125 s | -7.500 s (-9.42%) |
| Human interventions | 0 | 0 | 0 |

Total measured usage was `0.446453` credits and `151.750` seconds. The bounded-memory cell used 112,494 input tokens, including 91,648 cached, and 2,303 output tokens. The control used 114,553 input tokens, including 91,648 cached, and 2,232 output tokens.

Both valid implementations changed `roadmap.py` and `progress.py`, but their artifact hashes differed. Independent behavior, protected, and artifact checks accepted both, so the comparison does not assume one preferred implementation.

## Isolation and memory integrity

Each workspace retained only its selected workflow. Both copies of `phase-memory.json` matched the source SHA-256 digest `bfd76819f32a2711aa824afbd02c0def77621956f093690ae67c0777f17bea79`.

The treatment explicitly read the active specification and selected workflow, memory ledger, evidence contract, canonical source, and tests before reproducing and patching. Its ledger contains an unrelated patch-phase distractor that the declared capacity evicts. Independent verification and trajectory review found no implementation behavior traceable to that distractor or to unevidenced memory. This confirms the safety boundary, not that the model internally followed every retrieval step exactly.

## Trajectory review

The control trajectory has eight events and zero watchdog signals. The treatment trajectory has ten events: four read-only navigation or inspection actions, explicit reproduction, a two-file patch, validation, final diff inspection, the executor claim, and a passing independent audit.

The treatment watchdog emitted `repeated_action` for three separate repository-read commands and `stagnation` for the four-event unchanged-state navigation window. Human review labels both contextual false positives: these were distinct reads of the specification and workflow, memory ledger, evidence contract, and canonical source before any edit. No advice or intervention occurred.

Across the combined live calibration, `premature_patching` retains six false-positive labels, `stagnation` has three, and `repeated_action` has one. All have zero precision and no signal is eligible for an advisory experiment.

## Decision

The sentinel shows that both policies can complete this task safely within their ceilings. In this one pair, bounded memory used 3.59% fewer measured credits and 9.42% less wall time, but completion was identical. One pair cannot establish a reliable memory advantage, cost reduction, or causal effect.

Do not promote bounded phase memory from this result alone. The 18-cell repeated-seed campaign remains separately budgeted and approval-gated. Its expected information gain is stronger than the earlier adaptive-planning campaign because the sentinel direction is favorable, but the maximum spend should be reviewed before authorization.

## Evidence fingerprints

- Experiment report: `4f85190414e28fc5de1522e82999955ff3eee046b3515b5c6a9670d904c0b118`
- Control evaluation: `ef27a07d9a108f78a3d678ae57d34179f6e20b6c51a01551a68244d44970aa86`
- Treatment evaluation: `6b9273f9ca503b3f69a54adaaebe883b1048299cfba55d99e9f66a44df8c25e1`
- Control trajectory: `72efa1237b6f918afc37e99dcb856e68210fd8801cce7bdf80e079ce7cae6d79`
- Treatment trajectory: `6eb21b1bf3e6b3017d06d6da1fb5793f08a9234179a03ef2432783a52a4838cd`
- Treatment watchdog: `5cf9bf46064b7155325679d2ea5bee17d3b8801f6970fc121aa9d5b606172efb`
- Batch plan: `86f133f250b1bcfc494147f42c1ed432337f814034bc2095306620c025695d42`
- Live configuration: `8d3d37701f9ef3bc5c7e166a64121a408d3fecdec023cb9c0c712073ad143791`
- Execution inputs: `23c09c7d9128f1a0e77b7f79f91bd10e83d9504e463bf3f9d423251311050404`
