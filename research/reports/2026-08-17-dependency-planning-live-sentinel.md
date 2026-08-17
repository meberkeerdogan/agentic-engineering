# Dependency-Planning Live Sentinel

**Date:** 2026-08-17

**Model:** `gpt-5.6-luna` through the existing ChatGPT Codex login

**Batch:** `codex-planning-sentinel-001`

**Scope:** One diamond-shaped roadmap evolution task, one seed, one static-plan control, and one adaptive-plan treatment

## Result

The dependency-planning sentinel passed its safety gate. Both arms used isolated task copies and fresh plugin-free and MCP-free preflights. Each workspace retained only its selected planning workflow. Independent evaluation accepted every roadmap feature, protected test, and artifact check with no regressions, false completion, or human intervention.

| Measure | Static control | Adaptive treatment | Treatment delta |
| --- | ---: | ---: | ---: |
| Verified completion | 100% | 100% | 0 |
| Regressions | 0 | 0 | 0 |
| False completion | 0 | 0 | 0 |
| Estimated credits | 0.215307 | 0.257792 | +0.042485 (+19.73%) |
| Wall time | 71.266 s | 73.657 s | +2.391 s (+3.36%) |
| Human interventions | 0 | 0 | 0 |

Total measured usage was `0.473099` credits and `144.923` seconds. The adaptive cell used 166,786 input tokens, including 143,104 cached, and 2,261 output tokens. The static cell used 111,759 input tokens, including 90,624 cached, and 2,144 output tokens.

Both valid implementations changed `roadmap.py` and `progress.py`, but their final artifact hashes differed. Independent behavioral, protected, and artifact checks accepted both, so the comparison does not assume one preferred implementation.

## Trajectory review

Both privacy-safe trajectories contain navigation, a two-file patch, two test actions, diff inspection, the executor claim, and a successful independent audit. Each observe-only watchdog report emitted `premature_patching` and `stagnation`.

Both signal types are contextual false positives here. Each bound plan already marks reproduction complete, and the unchanged-state window covers the patch followed by read-only test and diff activity that ended in passing external verification. No advice or intervention occurred.

Across the combined live calibration, `premature_patching` now has six real labels and zero precision. `stagnation` has two real labels and zero precision. Neither signal is eligible for an advisory experiment.

## Decision

The sentinel establishes that both static and adaptive planning policies can pass the live safety boundary within their hard ceilings. It does not show that adaptive planning is better: both arms completed, while the adaptive cell was 19.73% more expensive and 3.36% slower in this single pair. Cost per additional verified completion is undefined because the completion delta is zero.

Do not promote adaptive planning from this result. The repeated-seed 18-cell campaign remains separately budgeted and approval-gated. Before considering it, weigh this zero-outcome-delta pair against the expected information gain and maximum spend.

## Evidence

Private raw evidence remains under ignored `.agentic-runs/live-batches/codex-planning-sentinel-001/` storage.

- Experiment report fingerprint: `e6b7f04af6731846ceaca0c9f25a7ab01825c86b7f9d96cbeaa6d511d8e56e52`
- Static evaluation fingerprint: `2853b178da127fedc89d797b97b9b657cad53a38b653763ad0dbb62653039cdc`
- Adaptive evaluation fingerprint: `0e3a9dd9d00114544ad044457d83f226de2a744ef5c8fd38df78a6483217b115`
- Execution fingerprint: `c50dfa4b7fbae75bb6b098914dc4d64b66402f5800f705eda29822ffd84eb87e`
- Plan fingerprint: `961b66a15f01d9d66b835bca75739369dac4f0ca87c9bc1372a3200f04fd84a3`
- Configuration fingerprint: `6a66e255457564579a44f85e284810eba6dcab1c14c6cdbf30f1614c2a46ca25`
