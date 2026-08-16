# M06h: Live Trajectory Capture

**Status:** Implemented

## Purpose

M06h connects completed live Codex cells to the existing M07 observe-only watchdog contract. It records what happened without advising, blocking, retrying, changing prompts, or affecting the experiment decision.

## Event mapping

Only completed structured Codex JSONL items are normalized:

- ordinary commands become `navigate` events;
- test commands before a file change become `reproduce` events;
- completed file changes become `patch` events;
- test commands after a file change become `validate` events;
- the adapter-recorded executor claim becomes a `complete` event;
- the independent evidence-contract result becomes a final `validate` audit event.

Started items and unstructured agent messages are excluded. The current CLI does not expose a reliable structured planning event, so this module does not infer plans from prose.

## Privacy and evidence boundary

`trajectory.json` contains normalized phases, actions, workspace-relative targets, state fingerprints, and evidence references. `trajectory-source.json` maps those steps to JSONL line numbers and item IDs.

Raw commands, command output, and agent messages remain only in the already-private `stdout.txt`; they are never copied into the source map. Every source map includes the raw file's SHA-256 so later review can detect replacement.

The initial and final state fingerprints cover durable workspace files while excluding `.git`, Python bytecode, and test caches. Intermediate file-change events use a deterministic hash chain over the preceding state and the structured changed-path metadata because the post-run JSONL does not contain historical file snapshots. This preserves change boundaries but cannot prove intermediate file contents or detect a later return to an earlier state; calibration must account for that limitation. File-change paths must remain inside the isolated workspace. Existing trajectory files cannot be overwritten.

Evidence contracts and their test code remain trusted inputs. The evaluator's `read_only` flag is a contract assertion, not operating-system containment, so a malicious test could still affect the post-audit workspace state.

## Live integration

Every M06f live cell now writes both capture files after independent evaluation and includes them in the cell's evidence references. A capture failure fails the cell while preserving the raw executor and evaluator evidence.

Capture version `1` is included in the live execution fingerprint. An in-progress batch therefore cannot resume across changed capture semantics.

## Promotion gate

- Navigation, reproduction, patch, validation, completion claim, and independent audit map deterministically.
- Commands, output, and messages are absent from redacted capture evidence.
- Generated trajectories and source maps validate against their schemas.
- Workspace escapes and evidence overwrites fail closed.
- Captured healthy fixture runs produce no watchdog signals.
- Live experiment tests prove every completed cell carries trajectory evidence.
- The full test suite makes no model calls.

M06h only collects calibration data and remains observe-only. M07b can construct calibration-gated advice, but the real sentinel calibration currently permits no signals; default advisory behavior still requires a separate controlled experiment.
