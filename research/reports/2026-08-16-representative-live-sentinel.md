# Representative Live Sentinel

**Date:** 2026-08-16

**Model:** `gpt-5.6-luna` through the existing ChatGPT Codex login

**Batch:** `codex-representative-sentinel-001`

**Scope:** One multi-file restock task, one seed, one bounded control, and one verified-loop treatment

## Result

The representative sentinel passed its safety gate. Both arms started from isolated copies, passed fresh plugin-free and MCP-free preflights, changed the required `inventory.py` and `reporting.py` files, passed all four independent evaluators, and recorded zero regressions, false completions, or human interventions. Both cells remained below the declared 0.5-credit and 300-second per-cell ceilings.

| Measure | Bounded control | Verified-loop treatment | Treatment delta |
| --- | ---: | ---: | ---: |
| Verified completion | 100% | 100% | 0 |
| Regressions | 0 | 0 | 0 |
| False completion | 0 | 0 | 0 |
| Estimated credits | 0.152644 | 0.176058 | +0.023414 (+15.34%) |
| Wall time | 82.671 s | 58.078 s | -24.593 s (-29.75%) |
| Human interventions | 0 | 0 | 0 |

The treatment used 88,788 input tokens, including 69,376 cached, and 1,477 output tokens. The control used 71,180 input tokens, including 53,248 cached, and 1,212 output tokens. Total measured usage was 0.328702 credits and total model time was 140.749 seconds.

The implementations were not byte-identical, but both independently satisfied the feature tests, protected existing behavior, and artifact checks. This is useful evidence that the evaluator accepted behavior rather than one preferred patch shape.

## Trajectory finding

M06h captured redacted trajectories for both cells. The source maps contained neither raw commands nor agent-message text. Each trajectory ended with an executor completion claim followed by a successful independent audit.

The observe-only watchdog emitted `premature_patching` once for each arm because neither ran a reproduction test before editing. The treatment performed a post-validation inspection step, but its workflow also explicitly places tests after implementation. The matching signals therefore require human calibration and should not be treated as proof that either run was defective. No watchdog intervention occurred.

This result demonstrates why observation must precede steering: a mechanically plausible rule can flag behavior that is consistent with the declared workflow and still leads to independently verified completion.

## Decision

The sentinel is promoted as safe enough to plan the next staged experiment, but it does not show that the verified loop is better. One paired task has no statistical power; both arms completed successfully, while the treatment traded 15.34% higher measured credits for 29.75% lower wall time in this run.

Do not enable advisory or blocking watchdog behavior from this sample. Label the two `premature_patching` cases during M07 calibration, then expand gradually to the multi-step evolution task and repeated seeds before considering the full 18-cell representative matrix.

## Evidence

Private raw evidence remains under ignored `.agentic-runs/live-batches/codex-representative-sentinel-001/` storage. Both preflights used a 14,718-byte clean prompt, zero enabled plugins, and zero MCP servers.

- Experiment report fingerprint: `44ff83ef84c0860f3ad146c9e813d02d8bb539f8a18e0b2c425afb6a37852215`
- Execution fingerprint: `769b27c332987e193516c083f1403019f848e2388b5899fcf9167d7b9e087efb`
- Plan fingerprint: `f3f5503230bc0dd218a9145cc861023c70b44f4bdfe2e7bd08f41cda1ec056d1`
- Configuration fingerprint: `6c43aaf50d1d0cce03d591d74e8b0abfb762d9cee435051787d7ab62dcf1d68e`

The result remains consistent with [Evaluating AGENTS.md](../papers/2602.11988-evaluating-agents-md.pdf): additional guidance can add usage without improving resolution, so workflow rules need repeated controlled measurement. The independent verification boundary also follows the risk highlighted by [Progress Mirage](../papers/2607.25152-progress-mirage.pdf): agent-reported completion is not sufficient evidence of actual progress.
