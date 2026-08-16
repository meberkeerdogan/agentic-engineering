# M09: Isolated Multi-Agent Runner

**Status:** Implemented; efficacy promotion remains experiment-gated

## Purpose

M09 executes explicit task adapters in isolated Git worktrees according to a dependency DAG. Independent ready tasks run concurrently up to a fixed limit. Downstream worktrees receive dependency commits before execution. Each task may change only declared paths, then receives a fixed-metadata commit. A separate integration worktree cherry-picks task commits in topological order and must pass a final non-mutating validation command.

The source worktree remains clean and unchanged. Reports contain commit IDs, changed paths, dependency waves, output hashes, validation evidence, conflicts, and human-intervention count without copying command output.

## Safety boundary

- Cycles and unknown dependencies fail before worktrees are created.
- Absolute or parent-traversing allowed paths are rejected.
- Undeclared changes, links, renames, nonzero tasks, conflicts, mutating validation, and failed validation stop integration.
- Commands use argument arrays and `shell=False`, but are trusted local adapters, not OS-sandboxed processes.
- Worktrees are retained as evidence; cleanup is an explicit later operation.
- The runner never selects or purchases an agent service. Paid adapters require separate authorization outside this module.

## Offline fixture

The fixture runs `alpha` and `beta` in parallel, supplies both commits to dependent task `combine`, integrates all three commits, and validates the combined artifact. It proves orchestration and isolation, not superiority over the single-agent baseline.

## Run

Point the manifest at trusted task adapters inside a clean target repository. The run root must be a new directory outside that repository.

```powershell
uv run python -m agentic_engineering.multi_agent path\to\multi-agent-run.json `
  --repository path\to\clean-repository `
  --run-root path\outside\repository\run-001 `
  --output multi-agent-report.json
```

## Promotion gate

Implementation is complete when isolation, dependency delivery, path constraints, integration, final validation, and reporting pass offline. Default use still requires an M06 comparison against the verified single-agent runner on tasks with genuinely independent work; no performance advantage is claimed yet.
