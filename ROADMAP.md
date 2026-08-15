# Roadmap

This roadmap is intentionally lightweight while the project is forming. It covers agent-engineering improvements broadly; playbooks, workflows, and skills are possible outputs rather than the limits of the project.

See [docs/implementation-plan.md](docs/implementation-plan.md) for the complete workflow, research choices, and delivery order.
See [docs/modules/README.md](docs/modules/README.md) for the module dependency map and promotion gates.

## Phase 0: Foundation

- Define core playbook, workflow, and skill vocabulary.
- Define the broader agent-engineering problem taxonomy and evaluation principles.
- Set up repository, license, and contribution process.
- Collect agent failure cases and candidate interventions from real coding-agent use.
- Select the first intervention to prototype based on expected value and measurability.

## Phase 1: Evidence and Definitions

- Establish baseline tasks, outcome measures, and experiment records.
- Define active-specification, evidence-contract, verified-state, and experiment-record schemas.
- Draft a portable playbook format.
- Draft a lightweight skill format.
- Create examples for planning, implementation, review, and handoff.
- Define how playbooks and skills declare tools, inputs, outputs, and verification.
- Document safe defaults for risky actions.

## Phase 2: First Working Intervention

- Build the smallest useful solution for the selected agent-engineering problem; this may be a runner, evaluator, harness, skill, or another form.
- Implement the simple baseline, then the verified single-agent manager-executor-auditor runner.
- Add structured logging.
- Add checkpoint and evaluator hooks.
- Compare it against a baseline on a small demo project and a realistic project.

## Phase 3: Integrations

- Experiment with adaptive planning, memory, observe-first monitoring, and paper reproduction.
- Add isolated multi-agent execution only after it beats the verified single-agent baseline.
- Explore adapters for popular coding-agent environments.
- Add examples for CI, local development, and review workflows.
- Publish contributor-friendly docs, starter templates, and skill examples.

## Open Questions

- What should the first runtime be?
- Which problem should the first implementation solve?
- What external evidence will demonstrate that it improves agent outcomes?
- Should playbook definitions be YAML, JSON, Markdown, code, or a hybrid?
- Should skills use the same format as playbooks or their own manifest?
- Which coding-agent tools should be supported first?
- How much state should a workflow persist between runs?
- What should be standardized, and what should stay tool-specific?
