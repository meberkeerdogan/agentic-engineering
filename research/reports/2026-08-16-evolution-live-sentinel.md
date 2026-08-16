# Multi-Step Evolution Live Sentinel

**Date:** 2026-08-16

**Model:** `gpt-5.6-luna` through the existing ChatGPT Codex login

**Batch:** `codex-evolution-sentinel-001`

**Scope:** One dependency-aware roadmap evolution task, one seed, one bounded control, and one verified-loop treatment

## Result

The evolution sentinel passed its safety gate. Both arms started from isolated copies, passed fresh plugin-free and MCP-free preflights, changed the required `roadmap.py` and `progress.py` files, and passed the feature tests, protected existing tests, and artifact checks. Neither arm produced regressions, false completion, or human intervention, and both stayed far below the declared 0.75-credit and 450-second per-cell ceilings.

| Measure | Bounded control | Verified-loop treatment | Treatment delta |
| --- | ---: | ---: | ---: |
| Verified completion | 100% | 100% | 0 |
| Regressions | 0 | 0 | 0 |
| False completion | 0 | 0 | 0 |
| Estimated credits | 0.163839 | 0.183771 | +0.019932 (+12.17%) |
| Wall time | 51.203 s | 75.094 s | +23.891 s (+46.66%) |
| Human interventions | 0 | 0 | 0 |

The treatment used 92,793 input tokens, including 73,472 cached, and 1,681 output tokens. The control used 72,231 input tokens, including 53,248 cached, and 1,410 output tokens. Total measured usage was 0.34761 credits and total model time was 126.297 seconds.

The two valid implementations were not byte-identical. Independent behavioral and regression checks accepted both, so the result does not depend on one preferred patch representation.

## Trajectory finding

Both M06h source maps excluded raw commands, outputs, and agent-message text. Each trajectory recorded a multi-file patch, validation, an executor completion claim, and a successful independent audit. The treatment recorded two validation actions after its patch; control recorded one.

The observe-only watchdog emitted `premature_patching` once for each arm because neither ran a reproduction test before editing. As in the earlier multi-file sentinel, both declared workflows place testing after implementation and all independent checks passed. These alerts require contextual labels and provide no basis for advice or intervention.

## Decision

The evolution sentinel is technically safe, but it does not show that the verified loop is better. Both arms succeeded, while treatment used 12.17% more measured credits and 46.66% more wall time in this single pair. With no completion difference, cost per additional verified completion is undefined.

Do not promote the treatment or watchdog advice from this sample. Add both trajectories to M07 calibration, then decide whether to collect repeated seeds. The full 18-cell matrix should remain gated until the accumulated sentinel evidence and expected information gain justify its maximum spend.

## Evidence

Private raw evidence remains under ignored `.agentic-runs/live-batches/codex-evolution-sentinel-001/` storage. Both preflights used zero enabled plugins and zero MCP servers.

- Experiment report fingerprint: `80da8fde07a2a9e238861056106b521bbc6b05b892c472ab8459d0c8ecdc2575`
- Execution fingerprint: `dd6a078fde6a44ba7302e62fada3fb6f3120737476e5189403effe2157756482`
- Plan fingerprint: `c55889aab6a750e2fcae359176b8cf94ade2e7ba36376a61e26eb1dfd6478541`
- Configuration fingerprint: `f81631c7a619434c77a8c23f43a730581cae99e652efcf9caf87cc4dad6f8c93`

The cost result again matches the caution from [Evaluating AGENTS.md](../papers/2602.11988-evaluating-agents-md.pdf): more workflow guidance can increase work without improving resolution. The successful independent audits preserve the externally grounded verification boundary motivated by [Progress Mirage](../papers/2607.25152-progress-mirage.pdf).
