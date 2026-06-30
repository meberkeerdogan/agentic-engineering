# Planning Loop Example

This is a sketch of a possible loop. It is not a final schema.

```yaml
name: planning-loop
purpose: Turn a feature request into an implementation plan.
inputs:
  - user_request
  - repository_context
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
