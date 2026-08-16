# Roadmap

This roadmap covers agent-engineering improvements broadly; playbooks, workflows, and skills are possible outputs rather than the limits of the project. The first implementation sequence is complete. Remaining work is evidence-driven promotion and extension, not unfinished core modules.

See [docs/implementation-plan.md](docs/implementation-plan.md) for the complete workflow, research choices, and delivery order.
See [docs/modules/README.md](docs/modules/README.md) for the module dependency map and promotion gates.

## Phase 0: Foundation

- **Complete:** vocabulary, project scope, governance, failure taxonomy, and initial research priorities.

## Phase 1: Evidence and Definitions

- **Complete:** baseline records, active-specification, evidence-contract, verified-state, experiment schemas, examples, playbooks, skills, and safe execution boundaries.

## Phase 2: First Working Intervention

- **Complete:** deterministic evaluators, append-only verified state, manager-executor-auditor runner, structured evidence, checkpoints, and the M06 control/treatment harness.
- **Evidence continues:** add more representative repositories, repeated seeds, and external replications before making broad efficacy claims.

## Phase 3: Integrations

- **Implemented experimentally:** adaptive dependency planning, bounded phase memory, observe-first monitoring, calibration-gated advice, independently reviewed property evidence, paper reproduction, and isolated multi-agent worktree integration.
- **Promotion-gated:** optional interventions and multi-agent execution stay off by default until they outperform the verified single-agent baseline without unacceptable regressions.
- **Next:** broaden agent adapters, CI examples, benchmark repositories, contributor templates, and independently reproducible experiments.

## Continuing Questions

- Which tasks and repositories best predict long-horizon production performance?
- Which experimental interventions earn default promotion, and for which task classes?
- Which coding-agent adapters should follow the existing Codex CLI adapter?
- What should be standardized across agents, and what should remain tool-specific?
- How much retained state improves outcomes without creating stale or misleading context?
