# v0.1 Release Acceptance

**Date:** 2026-08-21  
**Accepted commit:** `ae3cc33`  
**Result:** Pass for a source-distributed experimental `v0.1`

## Clean-copy check

The committed repository was exported with `git archive` into a new temporary
directory. Nothing from the working virtual environment was reused as project
source.

From that clean copy, the acceptance run:

1. created a new Python 3.11 virtual environment;
2. installed the project and test dependencies with `uv`;
3. loaded `agentic-engineering --help` from the installed command;
4. built both the source archive and wheel;
5. ran the UI, CLI, product, and schema tests.

Result: `73 passed`. The temporary checkout was then removed.

The complete repository suite was also run from the main workspace after the
acceptance export. Result: `304 passed` in `97.63s`.

## Browser and package evidence

- The local UI was checked at `1280x720` and `375x812`.
- The desktop and mobile layouts had no horizontal overflow.
- The browser reported no console warnings or errors.
- The wheel contains `index.html`, `app.css`, and `app.js`.
- The UI server rejects non-loopback binding and project-path escape attempts.
- UI tests confirm session-token and paid-run confirmation boundaries.

## What this acceptance did not prove

- It made no paid Codex call. Live model behavior is covered by the earlier pilot
  and experiment evidence, while this acceptance checks packaging and product
  wiring with an offline Codex double.
- It does not show that this workflow beats other coding-agent workflows.
- Another project still needs a prepared template, specification history, and
  trusted evidence contract.
- Codex is the only supported live adapter in this release.

These are declared `v0.1` limitations, not release-blocking defects.

## Publication boundary

The source product is ready enough for the first experimental release. Publishing
still requires an explicit version bump from `0.0.0` to `0.1.0`, final release-note
review, a `v0.1.0` tag, and GitHub/package publication. Those actions are kept
separate because they create the public release.
