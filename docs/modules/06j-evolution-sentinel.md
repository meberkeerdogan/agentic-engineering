# M06j: Multi-Step Evolution Sentinel

**Status:** Implemented; live sentinel completed

## Purpose

M06j prepares the next safety stage after the multi-file sentinel. It compares the bounded control and verified-loop treatment on one dependency-aware roadmap evolution task. The task coordinates changes across `roadmap.py` and `progress.py`, preserves existing behavior, and independently checks dependency readiness, blockers, and summary construction.

This remains a two-cell sentinel, not an efficacy experiment. It tests a harder task category before repeated seeds or the complete 18-cell representative matrix.

## Hard limits

- two declared cells in total and one cell per invocation;
- `0.75` credits per cell and `1.5` credits total;
- `450` seconds per cell and `900` seconds total;
- zero human interventions;
- fresh preflight, isolated workspace, independent evaluation, usage evidence, and redacted trajectory capture for every cell.

The larger ceiling reflects the additional dependency reasoning while remaining below one credit per cell. It is a hard upper bound, not an expected spend.

## Run boundary

The launcher is [`examples/evolution-sentinel-live.json`](../../examples/evolution-sentinel-live.json). Offline tests execute both arms with a local Codex double, but no authenticated cell is authorized by this module.

Each real invocation requires explicit approval describing the task, workflow arm, authenticated external service, 0.75-credit ceiling, and 450-second ceiling. The control must be reviewed before treatment is authorized.

## Promotion gate

- Both cells independently verify with zero regressions and false completion.
- Each cell remains inside its cost and time limits.
- Trajectory source maps contain no copied raw commands, outputs, or agent messages.
- Observe-only watchdog signals are reviewed and added to calibration before any advisory experiment.
- Results remain sentinel evidence; repeated seeds are still required for efficacy.

## Live result

Both cells independently verified with zero regressions and false completion. Control used `0.163839` credits in `51.203` seconds; treatment used `0.183771` credits in `75.094` seconds. Total usage was `0.34761` credits. Treatment was both more expensive and slower, and one paired task cannot support an efficacy claim.

Both observe-only trajectories again signalled patching before reproduction even though the declared workflows test after implementation and every independent check passed. The cases belong in calibration, not an intervention path. See the [evolution sentinel report](../../research/reports/2026-08-16-evolution-live-sentinel.md).
