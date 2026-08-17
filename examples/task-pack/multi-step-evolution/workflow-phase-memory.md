# Verified phase-memory workflow

<!-- memory-policy:start -->
Build the deterministic bounded view declared by `phase-memory.json` before patching. Exclude superseded and capacity-evicted entries, rank the current task and phase first, and rely only on retrieved entries whose evidence references agree with the canonical files.
<!-- memory-policy:end -->

## Shared verified execution core

1. Read `ACTIVE_SPEC.md`, `phase-memory.json`, and `evidence-contract.json` before editing.
2. Verify every remembered summary against its declared evidence reference before relying on it.
3. Reproduce the relevant failure and preserve protected behavior.
4. Implement only the requested change with no new dependencies.
5. Run the declared focused and protected tests after editing.
6. Inspect the final diff and claim completion only when independent evidence passes.

Do not edit the memory ledger, invent missing context, broaden the task, or treat your own completion claim as verification.
