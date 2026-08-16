# Verified dependency-planning workflow

<!-- planning-policy:start -->
Use the dependency graph as an evidence-driven plan. Among ready tasks, select the highest-priority item. After every completed or failed check, update your working task states, recompute the ready frontier, and skip work transitively blocked by failed evidence while continuing independent ready work.
<!-- planning-policy:end -->

## Shared verified execution core

1. Read `ACTIVE_SPEC.md`, `dependency-plan.json`, and `evidence-contract.json` before editing.
2. Keep brief working notes that map each plan task to direct evidence.
3. Implement only the requested change and respect dependency boundaries.
4. Run the declared tests after each completed plan task that has a validation edge.
5. Inspect the final diff and rerun all declared checks.
6. Claim completion only when every requirement has independent passing evidence and protected behavior still passes.

Do not broaden the task, add dependencies, edit the plan input, or treat your own completion claim as verification.
