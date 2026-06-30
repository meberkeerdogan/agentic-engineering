# Roadmap

This roadmap is intentionally lightweight while the project is forming.

## Phase 0: Foundation

- Define core loop vocabulary.
- Set up repository, license, and contribution process.
- Collect example workflows from real coding-agent use.
- Decide the first implementation runtime.

## Phase 1: Loop Definitions

- Draft a portable loop schema.
- Create example loops for planning, implementation, review, and handoff.
- Define how loops declare tools, inputs, outputs, and verification.
- Document safe defaults for risky actions.

## Phase 2: Runner Prototype

- Build a minimal loop runner.
- Add structured logging.
- Add checkpoint and evaluator hooks.
- Run sample loops against a small demo project.

## Phase 3: Integrations

- Explore adapters for popular coding-agent environments.
- Add examples for CI, local development, and review workflows.
- Publish contributor-friendly docs and starter templates.

## Open Questions

- What should the first runtime be?
- Should loop definitions be YAML, JSON, Markdown, code, or a hybrid?
- Which coding-agent tools should be supported first?
- How much state should a loop persist between runs?
- What should be standardized, and what should stay tool-specific?
