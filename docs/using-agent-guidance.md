# Using Agent Guidance Well

`AGENTS.md` is loaded as durable project guidance. Every rule can influence how an agent interprets future tasks, so unnecessary emphasis may cause the agent to over-focus on one concern or apply a rule where it does not help.

## Start small

Create the shortest file that improves collaboration. Add detail only after real use demonstrates a recurring need.

Good candidates include:

- essential project commands or repository facts
- confirmation boundaries
- reporting preferences
- stable conventions that repeatedly affect work

Keep one-off requests, temporary priorities, and task-specific constraints in the task prompt.

## Prefer broad guidance

Describe the default behavior and the important exception. Avoid long lists attempting to predict every situation.

For example, prefer:

> Proceed with ordinary in-scope local work. Ask before consequential external or difficult-to-reverse actions.

Over a large catalog of commands and edge cases that may quickly become incomplete or outdated.

## Add rules carefully

Before adding a rule, ask:

- Is this preference stable across many tasks?
- Has the issue happened repeatedly or would it be unusually costly?
- Could the wording make the agent ignore context or over-apply the rule?
- Is the rule personal, repository-wide, or limited to one directory?

Do not turn a single correction into permanent guidance automatically. Propose the change and review its likely effect first.

## Maintain the file

Review agent guidance occasionally. Remove stale, redundant, overly specific, or ineffective rules. Use nested `AGENTS.md` files only when an area genuinely needs different behavior.