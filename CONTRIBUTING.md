# Contributing

Thanks for helping build Agent Playbooks.

This project is early, so the most valuable contributions are clear problem statements, small working examples, design notes, and focused pull requests.

## Ways to Contribute

- Propose a playbook pattern for a real coding-agent workflow.
- Propose a reusable coding-agent skill.
- Improve docs, examples, or terminology.
- Add tests once implementation begins.
- Report confusing behavior or missing guardrails.
- Suggest integrations with coding-agent tools.

## Development Principles

- Make agent behavior inspectable.
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

The project has not chosen a runtime yet. Until then:

- keep examples in `examples/`
- keep playbook definitions in `playbooks/`
- keep reusable skills in `skills/`
- keep workflow definitions in `workflows/`
- keep design notes in `docs/`
- record architecture decisions in `docs/adr/`
- avoid adding large dependencies without an issue discussion

## Commit Style

Use clear, imperative commit messages:

```text
Add playbook definition glossary
Document evaluator lifecycle
Create first planning playbook example
```

## Code of Conduct

Participation in this project is covered by [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md).
