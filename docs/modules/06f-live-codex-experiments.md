# M06f: Live Codex Experiment Bridge

**Status:** Implemented

## Purpose

This bridge connects the M06e resumable matrix to the real M06b Codex adapter. Every control or treatment cell starts from its own copied repository, passes the M06d clean-environment preflight immediately before execution, and is judged by the declared independent evidence contract.

## Trust boundary

- The experiment plan fixes the arms, task repositories, workflow files, seeds, metrics, and adoption rule.
- The launcher fixes the model, sandbox, approval mode, timeout, rate card, environment policy, and task-to-evidence-contract binding.
- A SHA-256 execution fingerprint binds the launcher, rate card, environment policy, command, observed Codex CLI version, and byte-level task-template snapshots into the M06e state. A changed input cannot be mixed into a resumed batch.
- Each cell gets a fresh Git repository and temporary plugin-free Codex home.
- A cell workspace contains only its selected workflow file, so the control cannot discover treatment instructions and vice versa.
- M06d runs before every model call, not merely once at batch startup.
- Writable cells use explicit CLI auto-review. The CLI flag selects `workspace-write` and changes who reviews approval requests, not the filesystem or network permissions granted to the cell.
- Executor claims remain untrusted. Only the independent evidence contract can set verified completion.
- Completed cells emit redacted, observe-only M07 trajectories through the [M06h capture bridge](06h-live-trajectory-capture.md).
- Cell status stores exception types but not exception messages that may contain private output.
- The batch still refuses to repeat a cell left `running` by an interrupted paid process.

Private workspaces, prompt inspection, raw JSONL, evaluation reports, usage records, and batch state stay under ignored `.agentic-runs/` storage.

## Small comparison

The committed example contains one bounded task, one seed, one control, and one treatment. The batch permits one cell per invocation, so the first command runs the control and pauses at 1/2; the second runs the treatment and completes at 2/2.

```powershell
uv run python -m agentic_engineering.live_experiments examples/live-experiment.json --confirm-paid-run
```

`--confirm-paid-run` is mandatory because this command can consume subscription credits or API spend through the existing Codex login. The offline automated tests use a local Codex double and consume no credits.

This two-cell run validates the live comparison plumbing. It cannot establish that the treatment is generally better; that requires more representative tasks and repeated seeds declared before execution.

## Example treatment

The control performs one bounded implementation pass. The treatment explicitly maps requirements to checks, implements, runs tests, inspects the diff, and permits one focused correction before claiming completion. Both arms receive the same task and are evaluated by the same read-only evidence contract.

## Contracts

- [`live-experiment.schema.json`](../../schemas/live-experiment.schema.json) defines the live launcher.
- [`live-experiment-record.json`](../../examples/live-experiment-record.json) defines the two-cell comparison.
- [`live-batch-experiment.json`](../../examples/live-batch-experiment.json) limits the experiment to one paid cell per invocation.
