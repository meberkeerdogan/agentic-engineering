# Roadmap

This roadmap covers agent-engineering improvements broadly; playbooks, workflows, and skills are possible outputs rather than the limits of the project. The first implementation sequence is complete. Remaining work is evidence-driven promotion and extension, not unfinished core modules.

See [docs/implementation-plan.md](docs/implementation-plan.md) for the complete workflow, research choices, and delivery order.
See [docs/modules/README.md](docs/modules/README.md) for the module dependency map and promotion gates.

## v0.1 Product Finish Line

The core modules are complete. `v0.1` is ready when these five product tasks are complete:

1. Choose and freeze one supported default workflow: active specification, bounded execution, independent checks, and verified state.
2. Provide one simple command that sets up and runs that workflow without requiring users to understand the internal modules.
3. Provide one realistic end-to-end example showing the input, run, evidence, and final result.
4. Add short installation, configuration, troubleshooting, and output-reading guidance.
5. Run a clean user acceptance test from a fresh checkout, fix release-blocking problems, tag `v0.1.0`, and publish it.

This is the release boundary. Optional memory, adaptive planning, watchdog advice, property generation, multi-agent execution, extra adapters, and further paper reproductions do not block `v0.1`.

**2026-08-20 readiness decision:** the long-task research gate, regression-safe target scoring, Level 1 multi-target fixture, and Level 2 continuous-evolution fixture are complete. The product is ready to enter the five-task `v0.1` packaging stage above. It is not published yet. Additional held-out tasks and paid agent comparisons remain necessary before broad efficacy claims, but they do not block publishing the toolkit with clear experimental claims.

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
- **After v0.1:** broaden agent adapters, CI examples, benchmark repositories, contributor templates, and independently reproducible experiments only when they serve a chosen user or research need.

## Research Backlog

The remaining deep paper reviews, held-out long-task evaluations, external benchmark slices, and new methods continue as separate bounded research stages after—or alongside without delaying—the product finish line. Each stage may improve a later release, but no stage creates an automatic obligation to implement the next paper.

## Continuing Questions

- Which tasks and repositories best predict long-horizon production performance?
- Which experimental interventions earn default promotion, and for which task classes?
- Which coding-agent adapters should follow the existing Codex CLI adapter?
- What should be standardized across agents, and what should remain tool-specific?
- How much retained state improves outcomes without creating stale or misleading context?
