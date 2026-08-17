# Dependency-Planning Sentinel: Static Control

**Date:** 2026-08-17

**Model:** `gpt-5.6-luna` through the existing ChatGPT Codex login

**Batch:** `codex-planning-sentinel-001`

**Scope:** The static-plan control cell for one diamond-shaped roadmap evolution task and one seed. The adaptive treatment was not authorized or run.

## Result

The static control passed its safety gate. A fresh plugin-free and MCP-free preflight succeeded, the task ran in an isolated workspace containing `workflow-static-plan.md` but not `workflow-adaptive-plan.md`, and independent evaluation accepted every required feature, protected test, and artifact check.

| Measure | Static control | Hard ceiling |
| --- | ---: | ---: |
| Verified completion | 100% | Required |
| Regressions | 0 | 0 |
| False completion | 0 | 0 |
| Estimated credits | 0.215307 | 0.75 |
| Wall time | 71.266 s | 450 s |
| Human interventions | 0 | 0 |

Measured usage was 111,759 input tokens, including 90,624 cached input tokens, and 2,144 output tokens. This is one safety observation, not an efficacy comparison.

## Preflight and isolation

Codex `0.147.0` used ChatGPT authentication and confirmed `gpt-5.6-luna` availability. The clean temporary Codex home enabled zero plugins and zero MCP servers. Its 14,706-byte prompt inventory stayed below the 20,000-byte ceiling and was 64.07% smaller than the recorded normal-environment baseline. The preflight itself made no model call.

The source repository remained clean. Private raw output stays in ignored `.agentic-runs/live-batches/codex-planning-sentinel-001/` storage.

## Trajectory review

The privacy-safe trajectory contains navigation, a two-file patch, two test actions, diff inspection, the executor claim, and a successful independent audit. The observe-only watchdog emitted:

- `premature_patching`: labelled false positive because the bound static plan already marks reproduction complete and all independent checks passed;
- `stagnation`: labelled false positive because its unchanged-state window contains the patch followed by read-only testing and diff inspection, not a stuck repair loop.

The watchdog made no intervention. Adding this case brings `premature_patching` to five real labels, all false positives, so reaching the minimum support does not make it eligible for advice. `stagnation` has only one real label, also a false positive.

## Decision

The control satisfies the sentinel's technical and budget gates. The separately approved adaptive cell subsequently completed; see the [complete pair report](2026-08-17-dependency-planning-live-sentinel.md). No adaptive-planning advantage can be claimed from this control result.

## Evidence

- Independent evaluation fingerprint: `2853b178da127fedc89d797b97b9b657cad53a38b653763ad0dbb62653039cdc`
- Watchdog report fingerprint: `2949b0729297b8f996d89857e1cf2fa322244491388e020aaa0b7e16ff7a823a`
- Execution fingerprint: `c50dfa4b7fbae75bb6b098914dc4d64b66402f5800f705eda29822ffd84eb87e`
- Plan fingerprint: `961b66a15f01d9d66b835bca75739369dac4f0ca87c9bc1372a3200f04fd84a3`
- Configuration fingerprint: `6a66e255457564579a44f85e284810eba6dcab1c14c6cdbf30f1614c2a46ca25`
