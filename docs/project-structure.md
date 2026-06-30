# Project Structure

This repository starts with a documentation-first structure and leaves room for implementation once the first runtime is selected.

## Directories

- `.github/`: GitHub workflows, issue templates, and pull request template.
- `docs/`: Vision, architecture, design notes, and architecture decisions.
- `examples/`: Example loop definitions and usage sketches.
- `scripts/`: Developer automation helpers.
- `src/`: Future implementation code.
- `tests/`: Future automated tests.

## Adding New Areas

Add a new top-level directory only when it has a clear ownership boundary. Prefer starting with a README in the relevant existing directory until the project shape is clearer.
