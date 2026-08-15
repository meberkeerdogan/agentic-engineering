# Project Structure

This repository starts with a documentation-first structure and leaves room for multiple implementations. The current directories are starting points, not a restriction that all future work must be expressed as a playbook, workflow, or skill.

## Directories

- `.github/`: GitHub workflows, issue templates, and pull request template.
- `docs/`: Vision, architecture, design notes, and architecture decisions.
- `examples/`: Example interventions, experiments, playbooks, workflows, and skills.
- `playbooks/`: Reusable agent playbooks.
- `research/`: Primary-source PDFs, provenance, extraction tooling, and critical evidence reviews.
- `runners/`: Future workflow runner prototypes.
- `scripts/`: Developer automation helpers.
- `schemas/`: Shared schemas for playbooks, skills, workflows, and outputs.
- `skills/`: Reusable coding-agent skills.
- `src/`: Future implementation code.
- `tests/`: Future automated tests.
- `workflows/`: Reusable workflow definitions.

New top-level areas may be added for benchmarks, evaluators, harnesses, research reproductions, adapters, or other agent-engineering solutions once they have a clear ownership boundary. Research findings should be kept distinct from project defaults until a local reproduction or experiment supports adoption.

## Adding New Areas

Add a new top-level directory only when it has a clear ownership boundary. Prefer starting with a README in the relevant existing directory until the project shape is clearer.
