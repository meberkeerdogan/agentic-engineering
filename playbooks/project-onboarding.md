# Project Onboarding Playbook

Create simple agent guidance for a new or existing software project.

## Inputs

- Repository contents and existing documentation
- Human preferences about confirmation, reporting, decisions, and verification
- Existing agent instruction files, if any

## Outputs

- A reviewed root `AGENTS.md`
- Optional nested `AGENTS.md` files only where guidance genuinely differs
- An optional `project-preferences.json` record
- A short record of unresolved questions

## Workflow

1. **Inspect** — Discover the project structure, commands, and existing conventions.
2. **Interview** — Use the `create-agents-md` skill to ask a short set of behavioral preference questions.
3. **Summarize** — Show the broad rules that would be created and confirm their scope.
4. **Draft** — Create the smallest useful `AGENTS.md` from approved preferences and relevant project facts.
5. **Verify** — Check referenced paths and commands.
6. **Review** — Show the human the diff before finalizing.

## Simplicity checkpoint

Remove any rule that is speculative, task-specific, redundant, or likely to make the agent over-focus on one concern. Human review is required before personal preferences become shared repository guidance.

## Updating guidance

Propose small changes when preferences change or recurring friction demonstrates a real need. Do not grow the file after every interaction.