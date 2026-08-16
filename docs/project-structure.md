# Project Structure

This repository began with a documentation-first structure and now contains executable contracts, evaluators, runners, experiments, and research reproductions. The directories do not restrict future work to playbooks, workflows, or skills.

## Directories

- `.github/`: GitHub workflows, issue templates, and pull request template.
- `agentic_engineering/`: Executable Python modules and command-line entry points.
- `docs/`: Vision, architecture, design notes, and architecture decisions.
- `examples/`: Example interventions, experiments, playbooks, workflows, and skills.
- `playbooks/`: Reusable agent playbooks.
- `research/`: Primary-source PDFs, provenance, extraction tooling, and critical evidence reviews.
- `runners/`: Adapter and runner support assets.
- `scripts/`: Developer automation helpers.
- `schemas/`: Shared schemas for playbooks, skills, workflows, and outputs.
- `skills/`: Reusable coding-agent skills.
- `src/`: Package support files.
- `tests/`: Offline contract, safety, and integration tests.
- `workflows/`: Reusable workflow definitions.

New top-level areas may be added for benchmarks, evaluators, harnesses, research reproductions, adapters, or other agent-engineering solutions once they have a clear ownership boundary. Research findings should be kept distinct from project defaults until a local reproduction or experiment supports adoption.

## Adding New Areas

Add a new top-level directory only when it has a clear ownership boundary. Prefer extending an existing module or starting with a README in the relevant directory until the ownership boundary is proven.
