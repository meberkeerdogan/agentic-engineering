---
name: create-agents-md
description: Create or revise a simple AGENTS.md by inspecting a project and asking the human about confirmation, reporting, decision-making, and verification preferences. Use when starting a project, adding agent guidance to an existing repository, or simplifying guidance that has become too detailed.
---

# Create AGENTS.md

Create the smallest useful `AGENTS.md`. Prefer broad behavioral guidance over detailed rules that may make the agent over-focus on one concern.

## Workflow

1. Inspect existing agent files, contributor documentation, project commands, and repository structure. Do not ask the human for facts that can be discovered reliably.
2. Ask a short, adaptive interview about:
   - how often the agent should ask for confirmation and which conditions require it
   - whether reporting should be plain English, technical, or combined, and how often updates are useful
   - when the agent should make ordinary decisions independently versus present options
   - how verification and the final report should normally be handled
3. Let the human answer in their own words. Ask a follow-up only when an answer would create ambiguity or conflicting behavior.
4. Confirm whether each preference is personal, shared across the repository, or local to a subtree.
5. Summarize the proposed guidance before writing it.
6. Draft or update `AGENTS.md` using `assets/AGENTS.md.template`. Include only preferences the human approved and project facts that materially help agents work.
7. Verify referenced paths and commands when safe. Show the resulting diff for human review.

If the human wants a portable preference record, optionally write `project-preferences.json`. Otherwise, keep `AGENTS.md` as the single source of truth.

## Simplicity rules

- Start with as few rules as possible.
- Write broad defaults and meaningful exceptions instead of enumerating every scenario.
- Avoid rules based on hypothetical mistakes or one unusual interaction.
- Do not add mandatory plans, reports, checkpoints, or approval gates unless the human requests them.
- Keep task-specific instructions in the task prompt rather than permanent guidance.
- Link to existing documentation instead of copying it.
- Use nested `AGENTS.md` files only when a subtree genuinely needs different guidance.
- Do not interpret a preference as permission to expand the task or bypass normal safety boundaries.

## Updating guidance

Do not silently add a rule after one correction. When the human asks the agent to remember a preference or a problem clearly recurs, propose the smallest relevant change and explain how it could affect future behavior.