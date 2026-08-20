# M07d: Budgeted Phase-Memory Live Campaign

**Status:** Complete; 18 of 18 authenticated cells independently verified, default promotion rejected

## Purpose

This launcher turns the prepared 18-cell memory experiment into a resumable live campaign without authorizing any model call. It compares canonical rereading with bounded phase-aware memory across three task types and three seeds.

Only one cell may run per invocation. A completed cell is durably recorded before the launcher pauses, so later approvals resume the exact fingerprinted matrix without repeating earlier work.

## Budget

The two-cell memory sentinel averaged about `0.223` credits and `75.9` seconds per run. A direct 18-cell projection is approximately `4.02` credits and `22.8` minutes. Earlier valid task sentinels ranged from roughly `0.140` to `0.258` credits and `42.7` to `82.7` seconds per cell.

The campaign uses wider hard ceilings:

| Boundary | Per cell | Complete 18-cell matrix |
| --- | ---: | ---: |
| Credits | 0.5 | 9.0 |
| Model time | 300 seconds | 5,400 seconds (90 minutes) |
| Human interventions | 0 | 0 |

The total ceiling reserves the complete matrix, as required by the batch runner. It is not a spending target. The expected usage remains around four credits if the sentinel behavior generalizes.

## Offline validation

The local Codex test double completes all 18 cells through 18 resumable invocations. Tests verify:

- exactly one new cell per invocation;
- all three tasks, three seeds, and two workflow arms;
- independent verified completion with zero regressions;
- per-cell and total credit/time limits;
- fresh preflight evidence for every cell;
- nine isolated control workspaces and nine isolated memory workspaces;
- removal of the unselected workflow from every workspace;
- a complete report containing nine paired comparisons;
- zero authenticated model calls and zero credits.

## Live boundary

The launcher is [`examples/phase-memory-live.json`](../../examples/phase-memory-live.json), backed by [`examples/phase-memory-live-batch.json`](../../examples/phase-memory-live-batch.json).

Committing these files does not authorize execution. Before each live invocation, approval must identify the next declared task, workflow arm, authenticated Codex service, `0.5`-credit ceiling, and `300`-second ceiling. The launcher cannot run a second cell in the same invocation.

## Live progress

Cell 01, the canonical-rereading `median-fix` control at seed `0`, independently verified with zero regressions, false completion, watchdog signals, or human intervention. It used `0.179618` credits in `59.063` seconds. Workflow isolation and the immutable ledger hash both passed. See the [cell evidence report](../../research/reports/2026-08-17-phase-memory-campaign-cell-01.md).

Cell 02, the same control at seed `1`, also independently verified with zero regressions, false completion, watchdog signals, or human intervention. It used `0.153771` credits in `47.594` seconds, and its workflow and ledger isolation checks passed. See the [cell evidence report](../../research/reports/2026-08-18-phase-memory-campaign-cell-02.md).

Cell 03, the same control at seed `2`, independently verified with the same clean safety results. It used `0.196425` credits in `73.266` seconds. This completes all three low-pressure median control seeds without establishing a treatment comparison. See the [cell evidence report](../../research/reports/2026-08-18-phase-memory-campaign-cell-03.md).

Cell 04, the canonical-rereading `restock-report` control at seed `0`, independently verified all seven tests with no regressions or false completion. It used `0.213710` credits in `65.141` seconds. An observe-only stagnation alert was a contextual false positive caused by normal pre-edit inspection and made no intervention. See the [cell evidence report](../../research/reports/2026-08-18-phase-memory-campaign-cell-04.md).

Cell 05, the same control at seed `1`, independently verified the same seven tests with no regressions, false completion, watchdog signals, or intervention. It used `0.266027` credits in `85.140` seconds. See the [cell evidence report](../../research/reports/2026-08-18-phase-memory-campaign-cell-05.md).

Cell 06, the same control at seed `2`, independently verified the same seven tests with no regressions, false completion, or intervention. It used `0.239883` credits in `75.297` seconds. Two observe-only stagnation alerts were contextual false positives during normal investigation and validation. This completes the three-seed restock control block at a mean `0.239873` credits and `75.193` seconds. See the [cell evidence report](../../research/reports/2026-08-19-phase-memory-campaign-cell-06.md).

Cell 07, the canonical-rereading `roadmap-evolution` control at seed `0`, independently verified all six tests with no regressions or false completion. It used `0.249623` credits in `79.750` seconds. One observe-only stagnation alert was a contextual false positive caused by normal pre-edit investigation. See the [cell evidence report](../../research/reports/2026-08-19-phase-memory-campaign-cell-07.md).

Cell 08, the same control at seed `1`, independently verified the same six tests with no regressions, false completion, watchdog signals, or intervention. It used `0.202453` credits in `55.734` seconds. See the [cell evidence report](../../research/reports/2026-08-19-phase-memory-campaign-cell-08.md).

Cell 09, the same control at seed `2`, independently verified the same six tests with no regressions, false completion, watchdog signals, or intervention. It used `0.230847` credits in `78.266` seconds. This completes all nine controls with a 100% verified completion rate, zero regressions, and `1.932357` total measured credits. See the [cell evidence report](../../research/reports/2026-08-19-phase-memory-campaign-cell-09.md).

Cell 10, the bounded phase-memory `median-fix` treatment at seed `0`, independently verified all four tests with no regressions, false completion, watchdog signals, intervention, or memory-attributable error. It used `0.191772` credits in `57.297` seconds. Against its paired control, quality was equal, cost was `6.77%` higher, and time was `2.99%` lower. See the [cell evidence report](../../research/reports/2026-08-19-phase-memory-campaign-cell-10.md).

Cell 11, the same treatment at seed `1`, independently verified the same four tests with no regressions, false completion, watchdog signals, intervention, or memory-attributable error. It used `0.184539` credits in `54.640` seconds. Against its paired control, quality was equal, cost was `20.01%` higher, and time was `14.80%` higher. See the [cell evidence report](../../research/reports/2026-08-19-phase-memory-campaign-cell-11.md).

Cell 12, the same treatment at seed `2`, independently verified the same four tests with no regressions, false completion, watchdog signals, intervention, or memory-attributable error. It used `0.260437` credits in `61.250` seconds. Across the complete three-seed median block, treatment quality was equal, total cost was `20.18%` higher, and total time was `3.74%` lower. See the [cell evidence report](../../research/reports/2026-08-19-phase-memory-campaign-cell-12.md).

Cell 13, the bounded phase-memory `restock-report` treatment at seed `0`, independently verified all seven tests with no regressions, false completion, intervention, or memory-attributable error. It correctly excluded the obsolete decision and used the current one. Against its paired control, quality was equal, cost was `36.71%` higher, and time was `4.48%` higher. One observe-only stagnation alert was a contextual false positive during normal validation and diff inspection. See the [cell evidence report](../../research/reports/2026-08-19-phase-memory-campaign-cell-13.md).

Cell 14, the same treatment at seed `1`, independently verified the same seven tests with no regressions, false completion, watchdog signals, intervention, or memory-attributable error. It again excluded the obsolete decision. Against its paired control, quality was equal, cost was `26.05%` lower, and time was `33.84%` lower. Across two restock pairs, treatment cost is `1.91%` higher and time is `17.23%` lower, showing substantial seed-level variability. See the [cell evidence report](../../research/reports/2026-08-19-phase-memory-campaign-cell-14.md).

Cell 15, the same treatment at seed `2`, independently verified the same seven tests with no regressions, false completion, intervention, or memory-attributable error. It again followed the current decision and excluded the obsolete one. Across the complete three-seed restock block, treatment quality was equal, total cost was `0.14%` higher, and total time was `11.36%` lower. One observe-only stagnation alert was a contextual false positive during normal validation and diff inspection. See the [cell evidence report](../../research/reports/2026-08-19-phase-memory-campaign-cell-15.md).

Cell 16, the bounded phase-memory `roadmap-evolution` treatment at seed `0`, independently verified all six tests with no regressions, false completion, watchdog signals, intervention, or memory-attributable error. It correctly evicted the unrelated distractor and retained the roadmap evidence. Against its paired control, quality was equal, cost was `12.85%` lower, and time was `15.85%` lower. See the [cell evidence report](../../research/reports/2026-08-20-phase-memory-campaign-cell-16.md).

Cell 17, the same treatment at seed `1`, independently verified the same six tests with no regressions, false completion, watchdog signals, intervention, or memory-attributable error. It again evicted the distractor. Against its paired control, quality was equal, cost was `15.35%` higher, and time was `18.67%` higher. Across two roadmap pairs, treatment cost is `0.22%` lower and time is `1.65%` lower, showing opposite seed-level directions. See the [cell evidence report](../../research/reports/2026-08-20-phase-memory-campaign-cell-17.md).

Cell 18, the same treatment at seed `2`, independently verified all six tests with no regressions, false completion, watchdog signals, intervention, or memory-attributable error. It explicitly excluded the distractor. Across the complete roadmap block, treatment quality was equal, total cost was `0.22%` lower, and total time was `4.93%` lower. See the [final cell and campaign report](../../research/reports/2026-08-20-phase-memory-campaign-cell-18.md).

## Final result

All 18 cells independently verified. Both arms completed `9 / 9` tasks with zero regressions, false completions, or interventions. Across all tasks, treatment used `5.51%` more credits and `6.93%` less time. Across the six supersession and eviction pairs alone, cost was effectively equal and treatment time was `8.23%` lower, but completion remained equal.

The campaign is complete. Its deterministic report fingerprint is `82270bdbe8cf04b2af576cd6026f640ad4a3a737e03dc161aec3bdbcd2dff553`.

## Decision rule

Bounded memory is promoted only if the complete repeated evidence satisfies the predeclared experiment rule: improved verified completion on memory-pressure tasks, no loss on the low-pressure control, no memory-attributable errors or additional regressions, and acceptable cost, time, and intervention results.

The safety and overhead conditions passed, but the required completion improvement was `0.00` instead of at least `0.10`. Bounded phase memory therefore remains optional and experimental rather than becoming the default.
