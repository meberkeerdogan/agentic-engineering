# Planning Playbook Example

This is a sketch of a possible playbook. It is not a final schema.

```yaml
name: planning-playbook
purpose: Turn a feature request into an implementation plan.
inputs:
  - user_request
  - repository_context
workflow:
  steps:
    - id: understand
      goal: Restate the request and identify missing context.
    - id: inspect
      goal: Read the relevant files and current project conventions.
    - id: plan
      goal: Propose scoped implementation steps and verification.
  checkpoints:
    - after: plan
      type: human_review
outputs:
  - implementation_plan
  - open_questions
```
