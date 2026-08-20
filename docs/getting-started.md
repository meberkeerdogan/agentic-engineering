# Getting Started

Agentic Engineering `v0.1` has one supported product path. It copies a prepared
project into an isolated run directory, gives one coding task to Codex, checks the
result independently, and records whether the evidence actually verifies it.

The command line and browser UI call the same Python function. The UI is a simpler
front end, not a second workflow.

## What you need

- Python 3.11 or newer
- [uv](https://docs.astral.sh/uv/)
- Git
- the Codex CLI, already signed in, for a live run

Installation and tests do not spend model credits. A live run can use credits from
the authenticated Codex account and therefore requires a confirmation each time.

## Install and check the project

```powershell
git clone https://github.com/meberkeerdogan/agentic-engineering.git
cd agentic-engineering
uv sync --group test
uv run --group test pytest -q
```

## Use the local UI

```powershell
uv run agentic-engineering ui
```

The browser opens at `http://127.0.0.1:8765/`. The server accepts connections only
from the same computer, loads no remote assets, and sends no analytics.

Enter a project-relative configuration path and a new run ID. The included
example uses `examples/product-run.json`. Read the configuration before checking
the paid-run confirmation and pressing **Run verified workflow**.

Stop the local server with `Ctrl+C` in the terminal.

## Use the command line

This is the same operation without the browser:

```powershell
uv run agentic-engineering run examples/product-run.json `
  --run-id product-001 `
  --confirm-paid-run
```

The command exits with `0` only when independent evidence verifies the result. It
returns `1` when the agent finishes but verification rejects the work, and `2` for
invalid configuration or an unsafe run boundary.

## Read the result

The example writes `.agentic-runs/product-001/`. Start with:

| File | Meaning |
| --- | --- |
| `product-summary.json` | Short final status, regressions, cost, time, and evidence links |
| `active-spec.json` | The current requirements after revisions were applied |
| `evidence/evaluation-report.json` | Independent check results |
| `verified-state.json` | Current evidence-backed state |
| `verified-state.jsonl` | Tamper-evident history of state changes |
| `workspaces/median-fix/` | Isolated repository changed by the agent |

Compare the shape with
[`examples/expected-product-summary.json`](../examples/expected-product-summary.json).
That file is illustrative; its cost and time are not measured product claims.

`claimed_complete: true` means the executor said it finished.
`verified_complete: true` means the independent checks accepted the work. Only the
second value counts as success.

## Prepare another project

The current release runs a **prepared template**, not an arbitrary repository URL.
Put a clean copy of the target project inside the project root and add:

1. a `workflow.md` describing the bounded task;
2. a specification revision history;
3. an evidence contract containing trusted test commands;
4. a product configuration based on `examples/product-run.json`.

Change `template_ref`, `spec_history_ref`, `evidence_contract_ref`, the task fields,
model, and timeout for that project. Keep every referenced path inside the project
root. The runner copies the template before editing, so the original is not the
agent workspace.

This preparation is the main usability limitation of `v0.1`. A future setup wizard
can create these files, but it is not included until its behavior is designed and
tested.

## Common problems

- **Config file does not exist:** the UI path is relative to the directory where
  `--project-root` points.
- **Run ID already exists:** choose a new ID. Runs are never silently overwritten.
- **Codex preflight fails:** verify the CLI is installed and signed in, and that the
  model and dated rate card are current.
- **Verification rejects the result:** inspect the evaluation report and protected
  regression checks. Do not treat the agent's completion message as proof.
- **Port 8765 is busy:** use `agentic-engineering ui --port 8766`.

## Current product boundary

The default includes active specifications, isolated single-agent execution,
independent checks, regression-safe evaluation, verified state, and structured
evidence. Phase memory, adaptive planning, watchdog advice, generated property
evidence, multi-agent execution, and the Learning Companion remain optional
experiments. The UI does not enable them.
