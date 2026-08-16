# M06c: Private Live Pilot Runner

**Status:** Implemented

## Purpose

The live pilot runner turns the M06b adapter into one reusable command. It copies a deterministic task template into a private run directory, initializes a fresh Git repository, runs one bounded Codex control cell, evaluates it independently, and records usage-derived cost.

## Safety and evidence boundaries

- Every run ID is path-safe and immutable; an existing run is never overwritten.
- Templates, rate cards, and configuration must resolve inside the project root.
- Only `read-only` and `workspace-write` Codex sandboxes are accepted.
- Raw prompts, JSONL, stderr, evaluator output, and usage records stay under ignored `.agentic-runs/` storage.
- The committed example contains no credentials and the runner reuses the Codex CLI's existing authentication.
- `pilot-summary.json` reports the agent claim separately from independently verified completion.
- Pricing is an observation aid, not a billing statement. The dated rate card must be checked against its source before later experiments.

## Run

From the repository root:

```powershell
python -m agentic_engineering.live_pilot examples/live-pilot.json --run-id control-001
```

The initial example uses `gpt-5.6-luna` for a low-cost plumbing check. One successful run validates the integration; it does not establish that any workflow treatment is better. Treatment comparisons require the complete M06 control/treatment matrix.

The JSONL and usage fields consumed by the runner follow the official [Codex non-interactive mode documentation](https://learn.chatgpt.com/docs/non-interactive-mode). The example ChatGPT credit rates are dated `2026-08-16` and sourced from the official [Codex pricing documentation](https://learn.chatgpt.com/docs/pricing).
