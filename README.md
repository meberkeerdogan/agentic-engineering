# Agentic Engineering

Agentic Engineering is an open-source umbrella project for improving how AI agents perform software engineering. It develops and evaluates reusable methods, tools, and infrastructure for reliable agentic coding.

The project is not limited to loops, playbooks, workflows, or skills. Those are useful solution forms alongside evaluation harnesses, context and memory systems, specifications, orchestration strategies, safety controls, benchmarks, agent adapters, and new approaches discovered through research and experimentation.

## Project Status

Agentic Engineering is in early project setup. The current focus is identifying high-value agent-engineering problems, testing different solutions, and establishing shared foundations without prematurely locking the project to one runtime or abstraction.

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

See [docs/vision.md](docs/vision.md) and [docs/architecture.md](docs/architecture.md) for the starting design notes.

The planned delivery sequence and the research decisions behind it are in the [implementation plan](docs/implementation-plan.md).
The work is split into promotion-gated units in the [module dependency map](docs/modules/README.md).

## Repository Layout

```text
.
|-- .github/              GitHub workflows, issue templates, and PR template
|-- docs/                 Product, architecture, and decision records
|-- examples/             Example playbooks, workflows, and skill sketches
|-- playbooks/            Reusable agent playbooks
|-- research/             Reviewed papers, source provenance, and evidence reports
|-- runners/              Future runner prototypes
|-- scripts/              Developer automation helpers
|-- schemas/              Future shared schemas
|-- skills/               Reusable coding-agent skills
|-- src/                  Future implementation code
|-- tests/                Future automated tests
|-- workflows/            Reusable workflow definitions
|-- CHANGELOG.md          Release notes
|-- CONTRIBUTING.md       Contribution guide
|-- LICENSE               Project license
|-- ROADMAP.md            Early roadmap
|-- SECURITY.md           Security policy
```

## Getting Started

For now, start by reading:

1. [docs/vision.md](docs/vision.md)
2. [docs/architecture.md](docs/architecture.md)
3. [docs/implementation-plan.md](docs/implementation-plan.md)
4. [ROADMAP.md](ROADMAP.md)
5. [research/README.md](research/README.md)
6. [CONTRIBUTING.md](CONTRIBUTING.md)

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

## Contributing

Contributions are welcome. Before opening a pull request, read [CONTRIBUTING.md](CONTRIBUTING.md).

If you want to propose a major direction, open a GitHub issue first so the design can be discussed before implementation.

## License

Agentic Engineering is licensed under the MIT License. See [LICENSE](LICENSE).
