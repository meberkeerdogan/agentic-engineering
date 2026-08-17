# Verified phase-memory workflow

<!-- memory-policy:start -->
Treat `phase-memory.json` only as an immutable experiment ledger. Do not derive or use a bounded memory view. At each phase transition, re-read the canonical specification, source, tests, and evidence contract needed for the next action.
<!-- memory-policy:end -->

## Shared verified execution core

1. Read `ACTIVE_SPEC.md`, `phase-memory.json`, and `evidence-contract.json` before editing.
2. Verify every remembered summary against its declared evidence reference before relying on it.
3. Reproduce the relevant failure and preserve protected behavior.
4. Implement only the requested change with no new dependencies.
5. Run the declared focused and protected tests after editing.
6. Inspect the final diff and claim completion only when independent evidence passes.

Do not edit the memory ledger, invent missing context, broaden the task, or treat your own completion claim as verification.
