# M06i: Representative Live Sentinel

**Status:** Implemented and offline-validated

## Purpose

M06i inserts a two-cell sentinel between the successful one-task plumbing pilot and the full 18-cell representative experiment. It uses the new multi-file restock task once with the bounded control and once with the verified-loop treatment. This checks a new repository, multi-file editing, independent evaluation, usage metering, resumability, and M06h trajectory capture before a larger credit commitment.

The sentinel is a safety check, not an efficacy measurement. One task and one seed cannot establish that either workflow is better.

## Hard limits

- two declared cells in total;
- one cell per invocation;
- `0.5` credits per cell and `1.0` credit total;
- `300` seconds per cell and `600` seconds total;
- zero human interventions;
- the existing temporary Codex home, ChatGPT authentication, `gpt-5.6-luna`, workspace-write sandbox, and independent evidence contract.

The ceilings reserve the complete two-cell matrix before execution. A cell that exceeds its declared cost, time, or intervention limit is preserved as failed and the batch stops.

## Run

Each invocation can execute at most one paid cell:

```powershell
uv run python -m agentic_engineering.live_experiments `
  examples/representative-sentinel-live.json `
  --confirm-paid-run
```

Run the same command a second time only after reviewing the first cell's state, evidence, measured cost, and trajectory. The first invocation pauses after control; the second completes treatment and creates the comparison report.

## Promotion gate

- Both cells independently verify with zero regressions and false completion.
- Neither cell exceeds `0.5` credits or `300` seconds.
- Both cells contain redacted trajectory and source-map evidence.
- The first cell shows no integrity, privacy, or environment-boundary failure before treatment runs.
- Results are reported as sentinel evidence only; the full representative matrix remains separately gated.
