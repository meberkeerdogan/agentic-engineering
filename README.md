# Agentic Engineering

Agentic Engineering is an open-source umbrella project for improving how AI agents perform software engineering. It develops and evaluates reusable methods, tools, and infrastructure for reliable agentic coding.

The project is not limited to loops, playbooks, workflows, or skills. Those are useful solution forms alongside evaluation harnesses, context and memory systems, specifications, orchestration strategies, safety controls, benchmarks, agent adapters, and new approaches discovered through research and experimentation.

## Project Status

The research and engineering modules are complete and covered by offline tests. The frozen `v0.1` product path now combines active specifications, isolated single-agent execution, independent checks, regression-safe evaluation, and verified state behind one command and a local browser UI.

The toolkit is usable from source and has passed its [clean-checkout acceptance](docs/release-acceptance-v0.1.md), but it is not published as `v0.1.0` yet. The remaining release work is the version bump, final release-note review, tag, and package publication. New research methods and unfinished retrospective paper reviews are post-release work, not release blockers. See the finite [product finish line](ROADMAP.md#v01-product-finish-line).

Implementation does not imply that every mechanism is enabled by default. Watchdog advice, adaptive planning, phase memory, property evidence, and multi-agent execution remain promotion-gated until controlled comparisons show that they beat the simpler verified baseline on their declared targets.

## Why Agentic Engineering

Coding agents are powerful, but long-running work can become difficult to direct, inspect, reproduce, and trust. Agentic Engineering explores practical ways to improve the full engineering system around an agent:

- executable evaluations and externally grounded progress checks
- specifications, milestones, plans, and dependency-aware execution
- context, project memory, decision records, and handoffs
- agent harnesses, runners, adapters, and orchestration patterns
- safety controls, architectural invariants, and human checkpoints
- reusable playbooks, workflows, and skills where they are the right tool
- benchmarks and experiments that show whether an approach actually helps

## Initial Concepts

These are initial building blocks, not a closed product taxonomy:

- **Playbook**: A reusable guide for an agent task or family of tasks.
- **Workflow**: A complete agent process that may combine playbooks, skills, tools, and verification.
- **Skill**: A reusable instruction set, capability, or pattern an agent can apply.
- **Step**: One unit of work inside a workflow.
- **Checkpoint**: A place where progress is verified or reviewed.
- **Context**: The files, prompts, tool outputs, and decisions a workflow uses.
- **Handoff**: A structured summary that lets a person or another agent continue.
- **Evaluator**: A test, review, or rule that decides whether a workflow can continue.
- **Harness**: Runtime infrastructure that controls agent context, actions, state, verification, and recovery.
- **Experiment**: A reproducible comparison used to determine whether an agent-engineering intervention improves outcomes.

See [docs/vision.md](docs/vision.md) and [docs/architecture.md](docs/architecture.md) for the project vision and architecture notes.

The delivered sequence and the research decisions behind it are in the [implementation plan](docs/implementation-plan.md).
The work and its remaining evidence gates are summarized in the [module dependency map](docs/modules/README.md).
The concise [learning path](LEARNING_PATH.md) tracks completed concepts, the current experiment, exercises, and suggested next topics.

## Repository Layout

```text
.
|-- .github/              GitHub workflows, issue templates, and PR template
|-- agentic_engineering/  Executable Python modules and CLIs
|-- docs/                 Product, architecture, and decision records
|-- examples/             Schema-valid fixtures and runnable examples
|-- playbooks/            Reusable agent playbooks
|-- research/             Reviewed papers, source provenance, and evidence reports
|-- runners/              Adapter and runner support assets
|-- scripts/              Developer automation helpers
|-- schemas/              Versioned JSON contracts and reports
|-- skills/               Reusable coding-agent skills
|-- src/                  Package support files
|-- tests/                Offline contract, safety, and integration tests
|-- workflows/            Reusable workflow definitions
|-- AGENTS.md             Durable agent working and learning-report guidance
|-- CHANGELOG.md          Release notes
|-- CONTRIBUTING.md       Contribution guide
|-- LEARNING_PATH.md      Concise learner progress and exercise tracker
|-- LICENSE               Project license
|-- ROADMAP.md            Early roadmap
|-- SECURITY.md           Security policy
```

## Getting Started

Install with Python 3.11+, Git, and [`uv`](https://docs.astral.sh/uv/), then open the local interface:

```powershell
uv sync --group test
uv run agentic-engineering ui
```

The UI opens only on this computer and uses the same verified workflow as the command line. A live run uses the authenticated Codex CLI and may spend credits, so it requires an explicit confirmation. Follow the short [Getting Started guide](docs/getting-started.md) before the first run.

Run the included configuration directly with:

```powershell
uv run agentic-engineering run examples/product-run.json --run-id product-001 --confirm-paid-run
```

The current release expects a prepared project template with a specification and trusted evidence contract; it does not yet turn an arbitrary repository into a configured run automatically.

## Project and Research Guides

For deeper context, read:

1. [LEARNING_PATH.md](LEARNING_PATH.md)
2. [docs/vision.md](docs/vision.md)
3. [docs/architecture.md](docs/architecture.md)
4. [docs/implementation-plan.md](docs/implementation-plan.md)
5. [ROADMAP.md](ROADMAP.md)
6. [research/README.md](research/README.md)
7. [CONTRIBUTING.md](CONTRIBUTING.md)

The first working definition is the [project onboarding playbook](playbooks/project-onboarding.md). It uses the [`create-agents-md` skill](skills/create-agents-md/SKILL.md) to inspect a repository, ask a small set of preference questions, and draft a practical `AGENTS.md`.

Before adding permanent instructions, read [Using Agent Guidance Well](docs/using-agent-guidance.md).

The initial evidence base and critical review are available in the [research library](research/README.md). Research findings are treated as hypotheses to reproduce, not as automatic project defaults.

Run the current module test gate with Python 3.11+ and [`uv`](https://docs.astral.sh/uv/):

```powershell
uv run --group test pytest
```

Research-PDF verification has its own optional dependency group and command in [research/README.md](research/README.md#reproducibility).

Compile an ordered requirement history into one current active specification:

```powershell
uv run python -m agentic_engineering examples/spec-history-revised.json --output active-spec.json
```

Run the deterministic single-pass evaluation fixture:

```powershell
uv run python -m agentic_engineering.evaluators examples/fixture-task/evidence-contract.json --root examples/fixture-task
```

The [Codex CLI experiment adapter](docs/modules/06b-codex-cli-adapter.md) connects real, isolated `codex exec` runs to the experiment harness while keeping executor claims separate from independent verification. Its automated tests use an offline double and do not spend API credits.

Run one fresh, private control pilot with the CLI's existing authentication:

```powershell
uv run python -m agentic_engineering.live_pilot examples/live-pilot.json --run-id control-001
```

See the [private live pilot runner](docs/modules/06c-live-pilot-runner.md) and [clean Codex environment](docs/modules/06d-clean-codex-environment.md) before running it. Live output is ignored under `.agentic-runs/`; a no-credit preflight now checks the CLI, login, model, rate freshness, structured-output compatibility, plugin/MCP isolation, and prompt footprint before execution.

Run the offline resumable batch example twice to pause and then complete its four-cell matrix:

```powershell
uv run python -m agentic_engineering.batch_experiments examples/batch-experiment.json examples/experiment-observations.json
```

The [M06e batch runner](docs/modules/06e-resumable-batch-runner.md) enforces worst-case budgets, locks concurrent execution, preserves completed cells, and generates the normal deterministic experiment report. The replay example makes no model calls.

Run one explicitly confirmed live control or treatment cell through the clean Codex environment:

```powershell
uv run python -m agentic_engineering.live_experiments examples/live-experiment.json --confirm-paid-run
```

The [M06f live experiment bridge](docs/modules/06f-live-codex-experiments.md) creates a fresh repository per cell, preflights immediately before every model call, binds all execution inputs against resume-time drift, and independently evaluates the result. The command can consume Codex credits; its automated tests cannot.

The remaining offline modules are documented with runnable fixtures:

- [M07 optional interventions](docs/modules/07-optional-interventions.md): observe-first monitoring, calibration-gated advice, dependency planning, bounded phase memory, and independently reviewed property evidence.
- [M08 paper reproduction](docs/modules/08-paper-reproduction.md): hash-bound, claim-scoped reproduction with explicit deviations.
- [M09 isolated multi-agent orchestration](docs/modules/09-isolated-multi-agent.md): dependency-safe worktrees and separately validated integration.
- [M10 optional Learning Companion](docs/modules/10-learning-companion.md): fresh teaching-agent proposals bound to verified facts, focused files, decisions, and preserved failed experiments.

These offline fixtures make no paid model calls. M07, M09, and live Learning Companion adapters are experimental mechanisms, not default recommendations.

## Contributing

Contributions are welcome. Before opening a pull request, read [CONTRIBUTING.md](CONTRIBUTING.md).

If you want to propose a major direction, open a GitHub issue first so the design can be discussed before implementation.

## License

Agentic Engineering is licensed under the MIT License. See [LICENSE](LICENSE).
