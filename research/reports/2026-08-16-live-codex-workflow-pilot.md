# Live Codex Workflow Pilot

**Date:** 2026-08-16  
**Model:** `gpt-5.6-luna` through the existing ChatGPT Codex login  
**Valid batch:** `codex-workflow-comparison-003`  
**Scope:** One deterministic median-fix task, one seed, one control, and one treatment

## Result

The live experiment plumbing passed. Both arms started from isolated copies, passed a fresh plugin-free and MCP-free preflight, changed only `calculator.py`, produced the same final artifact hash, and passed all four independent tests with no regressions or human interventions.

| Measure | Bounded control | Verified-loop treatment | Treatment delta |
| --- | ---: | ---: | ---: |
| Verified completion | 100% | 100% | 0 |
| Regressions | 0 | 0 | 0 |
| False completion | 0 | 0 | 0 |
| Estimated credits | 0.139789 | 0.160657 | +0.020868 (+14.93%) |
| Wall time | 42.656 s | 51.031 s | +8.375 s (+19.63%) |
| Human interventions | 0 | 0 | 0 |

The treatment used 84,599 input tokens, including 66,304 cached, and 1,201 output tokens. The control used 70,589 input tokens, including 53,248 cached, and 882 output tokens.

## Decision

Do not claim that the verified-loop workflow is better. On this easy task, both workflows succeeded and the treatment cost slightly more. The predetermined rule was satisfied only as a plumbing gate: both arms verified with zero regressions and zero false completions.

The next efficacy experiment should use at least two repositories, multiple repeated runs, bounded issue tasks plus a multi-step evolution task, and a decision rule fixed before execution. This follows the experiment design in the [long-horizon reliability review](2026-08-14-long-horizon-reliability-review.md#first-reproduction-experiment). The independent evidence boundary should remain mandatory because [Progress Mirage](../papers/2607.25152-progress-mirage.pdf) found that agent-reported progress can diverge from externally measured progress.

## Launcher findings

Two earlier batches are excluded from the comparison but retained as private diagnostic evidence:

- Batch `001` consumed an estimated 0.145427 credits but was invalid because non-interactive approval routing prevented edits and tests. This exposed the need for explicit auto-review.
- Batch `002` consumed no model credits. CLI argument parsing rejected `--approve-for-me` together with `--sandbox`; the launcher now emits the mutually exclusive auto-review form and records its effective `workspace-write` mode.

The fixes were shipped in commits `c2ffbd7` and `4d0e33b`. All 180 repository tests passed before the valid batch ran. Across the valid comparison and the excluded model-using diagnostic, estimated usage was 0.445873 credits.

## Evidence

Private raw evidence remains under ignored `.agentic-runs/live-batches/` storage. The valid report has fingerprint `6de5b395aff429cf28dcc19f8d1742067f7419531719535aaf83cc9df9a69945`; its execution fingerprint is `7938336d7b466a143abb40142c32766269029e13318d396e95aa72e57d600a9c`.

The evidence design is also consistent with the local findings from [Evaluating AGENTS.md](../papers/2602.11988-evaluating-agents-md.pdf): extra instructions can add steps and cost without improving resolution, so workflow guidance should earn adoption through repeated measurement rather than intuition.
