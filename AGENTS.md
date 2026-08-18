# Agent Guidance

## Working style

- Continue ordinary in-scope engineering work autonomously. Ask only when an action needs new authority, is consequential outside the repository, or is difficult to reverse.
- Authenticated model calls that spend credits require a separately scoped approval naming the task, workflow arm, budget, and time limit.
- Treat implementation and controlled experiments as one evidence-driven process. Preserve unsuccessful experiments and explain what they ruled out or taught us.
- Commit and push each meaningful, verified stage as a focused change.

## Learning reports

Keep progress reports short and easy to read back to back. Use plain language, preserve only the context needed to follow the sequence, and avoid repeating details already recorded in linked files.

After each meaningful stage, include a brief **What you should learn from this stage** section in the progress report. Explain unfamiliar ideas in plain English before naming the technical term. Cover:

1. the main engineering concepts;
2. why the approach was selected and which realistic alternatives were considered;
3. how to interpret the implementation and results without overstating the evidence;
4. one small practical exercise;
5. a few questions the learner should be able to answer.

Whenever an exercise or review question is included, also provide a short answer or worked example so the learner can check their understanding immediately.

Point to a small set of files, functions, diagrams, or results rather than the whole repository. Keep [LEARNING_PATH.md](LEARNING_PATH.md) concise and update it only after meaningful milestones, not routine edits or individual troubleshooting steps.

When an enabled, verified learning-milestone packet exists, prefer the optional `LearningCompanionRunner` so a fresh teaching agent drafts the lesson from bounded evidence. Treat its output as a proposal: review it before updating `LEARNING_PATH.md`, and never let it verify or mutate engineering work. Use the inline learning report as the fallback when no companion adapter is configured.

## Research records

Treat the repository as both a product codebase and a research notebook. For every controlled experiment or important reproduction, preserve the question, predeclared method, model and environment, task and seed, budgets, positive or negative result, interpretation, limitations, decisions, and evidence fingerprints. Link the focused report from [research/PAPER_TRAIL.md](research/PAPER_TRAIL.md).

Keep raw evidence privacy-safe and retain failed or inconclusive runs. Do not rewrite earlier findings after later results arrive; append a correction or updated interpretation so the history remains suitable for audit, reproduction, and a future research paper.
