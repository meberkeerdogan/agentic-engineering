# Roadmap

This roadmap covers agent-engineering improvements broadly; playbooks, workflows, and skills are possible outputs rather than the limits of the project. The first implementation sequence is complete. Remaining work is evidence-driven promotion and extension, not unfinished core modules.

See [docs/implementation-plan.md](docs/implementation-plan.md) for the complete workflow, research choices, and delivery order.
See [docs/modules/README.md](docs/modules/README.md) for the module dependency map and promotion gates.

## v0.1 Product Finish Line

The core modules are complete. `v0.1` is ready when these five product tasks are complete:

1. **Complete:** choose and freeze one supported default workflow: active specification, bounded execution, independent checks, and verified state. See the [workflow](workflows/verified-single-agent-v0.1.md) and [product scope](docs/v0.1-product-scope.md).
2. **Complete:** provide one simple command and local UI that run the shared workflow without requiring users to understand the internal modules. See the [Getting Started guide](docs/getting-started.md).
3. **Complete:** provide one realistic end-to-end example showing the input, run, evidence, and final result. See [`product-run.json`](examples/product-run.json) and the [illustrative result](examples/expected-product-summary.json).
4. **Complete:** add short installation, configuration, troubleshooting, and output-reading guidance.
5. **Acceptance complete; publication pending:** the committed source was installed and built in a clean temporary checkout, `73` focused acceptance tests passed, and the full suite passed `304 / 304`. See the [acceptance record](docs/release-acceptance-v0.1.md). The version bump, `v0.1.0` tag, and publication remain explicit release actions.

This is the release boundary. Optional memory, adaptive planning, watchdog advice, property generation, multi-agent execution, extra adapters, and further paper reproductions do not block `v0.1`.

**2026-08-20 readiness decision:** the long-task research gate, regression-safe target scoring, Level 1 multi-target fixture, and Level 2 continuous-evolution fixture are complete. The product is ready to enter the five-task `v0.1` packaging stage above. It is not published yet. Additional held-out tasks and paid agent comparisons remain necessary before broad efficacy claims, but they do not block publishing the toolkit with clear experimental claims.

**2026-08-20 feature-freeze decision:** the supported `v0.1` product is now fixed to the verified single-agent workflow and its testing infrastructure. Optional interventions remain available for explicit research use but are disabled in the product default. The next release task is the one-command run path, not another mechanism.

**2026-08-21 product-interface milestone:** one shared Python interface now powers both `agentic-engineering run` and a loopback-only browser UI. The included prepared example, result shape, and usage guide complete finish-line items 2-4 without enabling experimental interventions.

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
