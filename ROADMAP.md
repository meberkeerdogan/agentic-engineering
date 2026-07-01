# Roadmap

This roadmap is intentionally lightweight while the project is forming.

## Phase 0: Foundation

- Define core playbook, workflow, and skill vocabulary.
- Set up repository, license, and contribution process.
- Collect example playbooks, workflows, and skills from real coding-agent use.
- Decide the first implementation runtime.

## Phase 1: Definitions

- Draft a portable playbook format.
- Draft a lightweight skill format.
- Create examples for planning, implementation, review, and handoff.
- Define how playbooks and skills declare tools, inputs, outputs, and verification.
- Document safe defaults for risky actions.

## Phase 2: Runner Prototype

- Build a minimal playbook runner.
- Add structured logging.
- Add checkpoint and evaluator hooks.
- Run sample playbooks against a small demo project.

## Phase 3: Integrations

- Explore adapters for popular coding-agent environments.
- Add examples for CI, local development, and review workflows.
- Publish contributor-friendly docs, starter templates, and skill examples.

## Open Questions

- What should the first runtime be?
- Should playbook definitions be YAML, JSON, Markdown, code, or a hybrid?
- Should skills use the same format as playbooks or their own manifest?
- Which coding-agent tools should be supported first?
- How much state should a workflow persist between runs?
- What should be standardized, and what should stay tool-specific?
