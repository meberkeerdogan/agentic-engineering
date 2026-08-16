# M06b: Codex CLI Experiment Adapter

**Status:** Implemented

## Purpose

M06 can compare fixed observations, but real experiments need a controlled way to execute coding agents. This adapter connects the harness to `codex exec` without letting an executor verify its own work.

The invocation is based on the official [Codex CLI command reference](https://developers.openai.com/codex/cli/reference/).

## Boundaries

- The trusted host supplies an isolated workspace, an independent evaluator, and an external cost meter.
- The prompt is sent through standard input instead of the process argument list.
- Each run uses `--ephemeral`, a declared `read-only` or `workspace-write` sandbox, and a JSON output schema.
- The provider-facing schema uses the supported structured-output subset; stricter checks such as unique artifact references are enforced again by the trusted local parser.
- `danger-full-access` and bypass flags are refused.
- JSONL standard output, standard error, request and process metadata, output schema, and final response are preserved per experiment cell.
- On Windows, the adapter resolves the installed `codex.cmd` shim explicitly and still invokes it with an argument array and `shell=False`.
- Existing cell evidence cannot be overwritten.
- Executor artifact references are untrusted strings. Evaluators must resolve and inspect artifacts independently.
- The CLI seed field labels repeated trials; it does not claim to control model randomness because the current CLI exposes no model-seed option.

## Trust Flow

```text
isolated workspace + bounded prompt
    -> codex exec
    -> untrusted completion claim
    -> independent evaluator
    -> external cost meter
    -> M06 RunObservation
```

Only `EvaluationOutcome.verified_complete` can set verified completion. A truthful-looking executor summary or `claimed_complete: true` can only contribute to the separately measured false-completion metric.

## Use

Construct `CodexExecRunner` with a workspace root and private evidence root. Then construct `CodexExperimentAdapter` with:

1. a resolver that prepares one isolated workspace per arm/task/seed cell;
2. an evaluator that checks the workspace without trusting the executor;
3. a meter that derives actual cost from provider or usage evidence.

`EvidenceContractEvaluator` is the concrete bridge to M03 read-only evidence contracts. `JsonlUsageCostMeter` reads only documented `turn.completed` usage events and prices them with a required, dated `UsageRates` record. Rates are never hardcoded into the adapter because API prices and ChatGPT credit rates can change.

The test suite uses an offline CLI double, so the promotion gate makes no model calls and spends no API credits.

For a reusable one-command control run built on this adapter, see [M06c: Private Live Pilot Runner](06c-live-pilot-runner.md).

## Promotion Gate

- The prompt travels through stdin and is represented in metadata only by a hash.
- Workspaces cannot escape the configured root.
- Unsafe sandbox modes fail before execution.
- Structured claims cannot mark their own run verified.
- Failed and malformed runs preserve evidence and fail closed.
- Cost must come from an explicit finite, non-negative measurement.
