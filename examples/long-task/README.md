# Long-Task Fixtures

These fixtures test connected engineering work without spending model credits.

- `multi-target-upgrade/` is the agent-visible Level 1 repository.
- `evaluators/multi-target-upgrade/` contains hidden target and regression checks. It must not be copied into an agent workspace.
- `oracles/multi-target-upgrade/solution.patch` is the known-good implementation used only to prove that the task and evaluator agree.

The starting repository contains nine Python source files and more than 500 source lines. Its five upgrade targets touch inventory ranking, order allocation, shipping, reporting, and service integration.
