# Agent Playbooks

Agent Playbooks is an open-source project for reusable playbooks, workflows, and skills for coding agents.

The goal is to make agent work easier to repeat, inspect, improve, and share. The repository can hold playbook definitions, reusable skills, schemas, runners, examples, and documentation that help people build more reliable coding-agent workflows.

## Project Status

Agent Playbooks is in early project setup. The current focus is shaping the core concepts, repository structure, and contribution process before locking in a runtime or package format.

## Why Agent Playbooks

Coding agents are powerful, but their work can become hard to trust when the process is invisible. Agent Playbooks aims to make the process explicit:

- repeatable playbooks for common agent tasks
- reusable skills that package agent behavior and instructions
- checkpoints for human review and agent self-review
- verification steps that run tests, linters, or custom checks
- records of decisions, assumptions, and handoffs
- portable definitions and examples that teams can adapt

## Initial Concepts

- **Playbook**: A reusable guide for an agent task or family of tasks.
- **Workflow**: A complete agent process that may combine playbooks, skills, tools, and verification.
- **Skill**: A reusable instruction set, capability, or pattern an agent can apply.
- **Step**: One unit of work inside a workflow.
- **Checkpoint**: A place where progress is verified or reviewed.
- **Context**: The files, prompts, tool outputs, and decisions a workflow uses.
- **Handoff**: A structured summary that lets a person or another agent continue.
- **Evaluator**: A test, review, or rule that decides whether a workflow can continue.

See [docs/vision.md](docs/vision.md) and [docs/architecture.md](docs/architecture.md) for the starting design notes.

## Repository Layout

```text
.
|-- .github/              GitHub workflows, issue templates, and PR template
|-- docs/                 Product, architecture, and decision records
|-- examples/             Example playbooks, workflows, and skill sketches
|-- playbooks/            Reusable agent playbooks
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
3. [ROADMAP.md](ROADMAP.md)
4. [CONTRIBUTING.md](CONTRIBUTING.md)

Once the first runtime is chosen, this section will include install, build, and test commands.

## Contributing

Contributions are welcome. Before opening a pull request, read [CONTRIBUTING.md](CONTRIBUTING.md).

If you want to propose a major direction, open a GitHub issue first so the design can be discussed before implementation.

## License

Agent Playbooks is licensed under the MIT License. See [LICENSE](LICENSE).
