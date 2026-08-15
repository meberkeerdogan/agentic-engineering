# Contributing

Thanks for helping build Agentic Engineering.

This project is early, so the most valuable contributions are clear problem statements, small working examples, design notes, and focused pull requests.

## Ways to Contribute

- Document a recurring agentic-engineering problem with evidence.
- Propose or implement a harness, evaluator, benchmark, playbook, workflow, skill, memory system, adapter, or other intervention.
- Reproduce relevant research and test whether its findings transfer to real projects.
- Improve docs, examples, or terminology.
- Add tests once implementation begins.
- Report confusing behavior or missing guardrails.
- Suggest integrations with coding-agent tools.

## Development Principles

- Make agent behavior inspectable.
- Measure improvements against explicit baselines and external outcomes.
- Prefer small, composable primitives over large hidden workflows.
- Treat verification as part of the workflow, not an afterthought.
- Keep humans in control of risky decisions.
- Document assumptions and handoffs clearly.

## Pull Request Process

1. Open an issue for major design or architecture changes.
2. Keep pull requests focused on one idea.
3. Update docs when behavior, concepts, or public APIs change.
4. Add or update tests for implementation changes.
5. Fill out the pull request template honestly.

## Local Development

The first implementation modules use Python 3.11+ and `uv`, while the portable contracts remain runtime-agnostic:

- keep examples and small experiments in `examples/`
- keep playbook definitions in `playbooks/`
- keep reusable skills in `skills/`
- keep workflow definitions in `workflows/`
- keep design notes in `docs/`
- record architecture decisions in `docs/adr/`
- add a well-named area when a solution does not fit the existing categories
- avoid adding large dependencies without an issue discussion

Run the current automated checks with:

```powershell
uv run --group test pytest
```

## Commit Style

Use clear, imperative commit messages:

```text
Add playbook definition glossary
Document evaluator lifecycle
Create first planning playbook example
```

## Code of Conduct

Participation in this project is covered by [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md).
