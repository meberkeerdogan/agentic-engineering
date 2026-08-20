# Verified Single-Agent Workflow v0.1

**Status:** Frozen for `v0.1`

This is the one supported default workflow for the first release. Its purpose is
simple: let one coding agent attempt bounded work, then use separate evidence to
decide whether the work is actually complete.

## Required flow

1. **Compile the current specification.** Use trusted requirements and explicit
   revisions to produce one active specification. Superseded requirements remain
   traceable but cannot silently become active again.
2. **Select one bounded work item.** The item and its dependencies are declared
   before execution. Only dependency-ready work may start.
3. **Run a fresh executor.** The executor may change the isolated project and
   submit artifacts plus a completion claim. It cannot verify its own work.
4. **Run an independent audit.** A separate auditor applies the trusted evidence
   contract. Required checks and protected existing behavior are both evaluated.
5. **Record verified state.** The append-only state log advances the item only
   when the evidence is valid, all required checks pass, and no protected behavior
   regresses. Failure, blocking, and retry are recorded explicitly.
6. **Return inspectable output.** The run reports the active specification,
   submitted artifacts, evaluation results, verified state, and a concise final
   status. An agent claim is shown as a claim, never as proof.

## Required rules

- Execution is isolated from the user's source project when an adapter can make
  changes.
- Retries are explicit and bounded; each retry receives a fresh executor.
- Evidence commands come from trusted project configuration and run without a
  shell.
- Missing, malformed, mismatched, or regressing evidence fails closed: the work
  cannot become verified.
- Live provider calls require an explicit confirmation, budget, and time limit.
- The first supported live adapter is the authenticated Codex CLI adapter. The
  deterministic offline path remains available for tests and examples.

## Supported testing capability

Evidence may be grouped into named targets so users can see partial completion.
The strict target score becomes zero when protected existing behavior breaks.
Controlled comparisons may use the experiment harness, but experiments are not a
hidden part of an ordinary product run.

## Not part of the default

Phase memory, adaptive planning, watchdog advice, generated property evidence,
multi-agent execution, and the Learning Companion are optional experiments. A
normal `v0.1` run must not enable them implicitly.

## Frozen interface for the product command

The next packaging stage will expose this workflow through one command. The
command will accept a project, an active-specification input or revision history,
trusted evidence configuration, bounded run settings, and an adapter selection.
It will produce a run directory containing the specification, evidence, state,
and final summary, and it will return a non-zero exit status when the work is not
verified.

Changes to this workflow before `v0.1.0` are limited to release-blocking
correctness, safety, or usability fixes. New interventions remain outside this
workflow until they pass the promotion rule in the product scope.
