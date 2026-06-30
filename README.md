# Loops

Loops is an open-source project for building reliable feedback loops around coding agents.

The goal is to make agent work easier to repeat, inspect, improve, and share. A loop can describe how an agent plans, edits, verifies, reviews, records decisions, and hands work back to a person or another agent.

## Project Status

Loops is in early project setup. The current focus is shaping the core concepts, repository structure, and contribution process before locking in a runtime or package format.

## Why Loops

Coding agents are powerful, but their work can become hard to trust when the process is invisible. Loops aims to make the process explicit:

- repeatable workflows for common agent tasks
- checkpoints for human review and agent self-review
- verification steps that run tests, linters, or custom checks
- records of decisions, assumptions, and handoffs
- portable loop definitions that teams can adapt

## Initial Concepts

- **Loop**: A repeatable workflow for an agent.
- **Step**: One unit of work inside a loop.
- **Checkpoint**: A place where progress is verified or reviewed.
- **Context**: The files, prompts, tool outputs, and decisions a loop uses.
- **Handoff**: A structured summary that lets a person or another agent continue.
- **Evaluator**: A test, review, or rule that decides whether a loop can continue.

See [docs/vision.md](docs/vision.md) and [docs/architecture.md](docs/architecture.md) for the starting design notes.

## Repository Layout

```text
.
|-- .github/              GitHub workflows, issue templates, and PR template
|-- docs/                 Product, architecture, and decision records
|-- examples/             Example loops and usage sketches
|-- scripts/              Developer automation helpers
|-- src/                  Future implementation code
|-- tests/                Future automated tests
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

Loops is licensed under the MIT License. See [LICENSE](LICENSE).
