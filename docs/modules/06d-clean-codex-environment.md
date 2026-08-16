# M06d: Clean Codex Experiment Environment

**Status:** Implemented

## Purpose

The clean-environment module prevents avoidable experiment contamination and blocks paid execution until local compatibility checks pass. It creates a temporary Codex home containing only a short-lived copy of the existing ChatGPT authentication, so installed plugins, personal skills, MCP servers, and unrelated global instructions are not loaded into the experiment process.

The base Codex configuration is normally read from `~/.codex/config.toml`, while named profiles overlay that base instead of replacing it. A separate temporary home is therefore the reliable isolation boundary for this experiment. See the official [configuration reference](https://learn.chatgpt.com/docs/config-file/config-reference) and [advanced configuration guide](https://learn.chatgpt.com/docs/config-file/config-advanced).

## No-credit preflight

Before `codex exec`, the runner verifies:

- the installed CLI meets the declared minimum version;
- authentication is an existing ChatGPT login;
- the selected model appears in the local Codex model catalog;
- the external rate card matches the model, is not future-dated, and is fresh enough;
- the structured-output schema avoids known unsupported keywords;
- the temporary home has zero enabled plugins and zero enabled MCP servers;
- the exact model-visible prompt is below the declared JSON-byte budget.

These checks use local CLI inspection commands and do not perform a model call. A passing `preflight-report.json` is stored with private run evidence. The raw prompt and authentication data are never written to that report.

## Authentication lifecycle

The temporary home is created below the existing Codex `tmp` directory, inherits that directory's access controls, and applies user read/write mode where the operating system supports it. The authentication copy is removed in a `finally`-style context cleanup after success or failure. It is never committed. If the host process is forcibly killed, remove any leftover `agentic-engineering-*` directory below the Codex `tmp` directory before continuing.

## Initial measurement

On the development machine, the implemented no-credit preflight measured 41,320 JSON bytes in the normal environment and 14,488 bytes in the clean environment: a 26,832-byte, or 64.94%, reduction. This is a context-footprint measurement, not a token-usage claim. A later paid control run is required to compare actual input tokens with the earlier 128,737-token pilot.

The committed policy is [`examples/codex-environment.json`](../../examples/codex-environment.json). Tighten its prompt budget only after measurements on other machines show a portable lower threshold.
