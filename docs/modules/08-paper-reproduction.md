# M08: Paper Reproduction Toolkit

**Status:** Implemented with one traceable claim-level reproduction

## Purpose

M08 turns a paper claim into an executable, auditable record: exact paper artifact, claim and page, lineage, locked environment, local experiment, acceptance rubric, results, and deviations. Artifact hashes and the complete manifest fingerprint prevent silent source replacement.

The first reproduction targets Progress Mirage's structural claim that agent-reported completion can diverge from external verification. A trusted deterministic fixture emits a completion claim and an independent rejection; the rubric confirms the divergence. The result is `supported_in_fixture`, not a full-paper replication.

## Safety and honesty boundary

Commands use argument arrays with `shell=False`, a fixed working directory, and a timeout. Paths cannot escape the project and linked artifacts are rejected. The manifest declares network and model calls disabled, but this is not an OS network sandbox; only trusted reproduction commands may run.

Every deviation states its impact. The fixture does not reproduce the paper's long-running agent testbed, behavioral frequencies, judge comparisons, or effect sizes.

## Run

```powershell
uv run python -m agentic_engineering.paper_reproduction `
  research/reproductions/progress-mirage-claim/reproduction.json `
  --project-root . `
  --output reproduction-report.json
```

## Promotion gate

- Exact paper, fixture, and environment hashes are verified.
- The experiment reproduces byte-stable structured observations.
- Every rubric criterion passes and cites evidence.
- Deviations prevent broader claims than the evidence supports.
- Tampered sources, path escapes, changed observations, and nonzero commands fail closed.
- The complete suite remains offline and deterministic.
