"""No-credit preflight and temporary clean home for Codex experiments."""

from __future__ import annotations

import json
import os
import re
import shutil
import stat
import subprocess
import tempfile
from collections.abc import Mapping, Sequence
from contextlib import AbstractContextManager
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any

from .codex_adapter import SUBMISSION_SCHEMA, resolve_command_prefix
from .codex_evidence import UsageRates


class CodexEnvironmentError(RuntimeError):
    """Raised before a paid run when the Codex environment is not trustworthy."""


ENVIRONMENT_FIELDS = {
    "version",
    "isolation",
    "authentication",
    "minimum_codex_version",
    "maximum_rate_age_days",
    "maximum_prompt_json_bytes",
    "preflight_timeout_seconds",
    "measure_baseline_prompt",
}
VERSION_PATTERN = re.compile(r"\bcodex-cli\s+(\d+)\.(\d+)\.(\d+)\b")
UNSUPPORTED_STRUCTURED_OUTPUT_KEYWORDS = {"uniqueItems"}


def _positive_number(value: Any, label: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)) or value <= 0:
        raise CodexEnvironmentError(f"{label} must be a positive number")
    return float(value)


@dataclass(frozen=True)
class CodexEnvironmentPolicy:
    """Committed requirements for a clean Codex experiment process."""

    minimum_codex_version: tuple[int, int, int]
    maximum_rate_age_days: int
    maximum_prompt_json_bytes: int
    preflight_timeout_seconds: float
    measure_baseline_prompt: bool

    @classmethod
    def from_mapping(cls, value: Mapping[str, Any]) -> "CodexEnvironmentPolicy":
        if set(value) != ENVIRONMENT_FIELDS or value.get("version") != 1:
            raise CodexEnvironmentError(
                "Codex environment policy must contain exactly the version 1 fields"
            )
        if value.get("isolation") != "temporary-codex-home":
            raise CodexEnvironmentError("Codex isolation must be temporary-codex-home")
        if value.get("authentication") != "chatgpt":
            raise CodexEnvironmentError("Codex authentication must be chatgpt")
        version = value.get("minimum_codex_version")
        if not isinstance(version, str) or not re.fullmatch(r"\d+\.\d+\.\d+", version):
            raise CodexEnvironmentError("minimum Codex version must be numeric x.y.z")
        age = value.get("maximum_rate_age_days")
        if isinstance(age, bool) or not isinstance(age, int) or not 0 <= age <= 365:
            raise CodexEnvironmentError("maximum rate age must be an integer from 0 to 365")
        prompt_bytes = value.get("maximum_prompt_json_bytes")
        if (
            isinstance(prompt_bytes, bool)
            or not isinstance(prompt_bytes, int)
            or prompt_bytes <= 0
        ):
            raise CodexEnvironmentError("maximum prompt JSON bytes must be a positive integer")
        timeout = _positive_number(
            value.get("preflight_timeout_seconds"), "preflight timeout"
        )
        if timeout > 120:
            raise CodexEnvironmentError("preflight timeout may not exceed 120 seconds")
        measure = value.get("measure_baseline_prompt")
        if not isinstance(measure, bool):
            raise CodexEnvironmentError("measure_baseline_prompt must be a boolean")
        return cls(
            tuple(int(part) for part in version.split(".")),
            age,
            prompt_bytes,
            timeout,
            measure,
        )


class TemporaryCodexHome(AbstractContextManager[Path]):
    """Use existing ChatGPT auth in a plugin-free home, then remove the copy."""

    def __init__(self, source_home: Path | None = None):
        configured = os.environ.get("CODEX_HOME")
        self.source_home = (
            Path(source_home)
            if source_home is not None
            else Path(configured) if configured else Path.home() / ".codex"
        ).resolve()
        self.path: Path | None = None

    def __enter__(self) -> Path:
        auth_source = self.source_home / "auth.json"
        temp_parent = self.source_home / "tmp"
        if not auth_source.is_file():
            raise CodexEnvironmentError("Codex auth.json is required for ChatGPT preflight")
        if not temp_parent.is_dir():
            raise CodexEnvironmentError("Codex temporary directory does not exist")
        self.path = Path(
            tempfile.mkdtemp(prefix="agentic-engineering-", dir=temp_parent)
        ).resolve()
        auth_copy = self.path / "auth.json"
        try:
            shutil.copyfile(auth_source, auth_copy)
            os.chmod(auth_copy, stat.S_IRUSR | stat.S_IWUSR)
        except OSError as error:
            shutil.rmtree(self.path, ignore_errors=True)
            self.path = None
            raise CodexEnvironmentError(
                "could not prepare temporary Codex authentication"
            ) from error
        return self.path

    def __exit__(self, exc_type: Any, exc_value: Any, traceback: Any) -> None:
        if self.path is not None:
            shutil.rmtree(self.path)
            self.path = None


def _environment(codex_home: Path | None) -> dict[str, str]:
    environment = os.environ.copy()
    if codex_home is not None:
        environment["CODEX_HOME"] = str(codex_home)
    return environment


def _run_codex(
    command_prefix: tuple[str, ...],
    arguments: Sequence[str],
    *,
    cwd: Path,
    codex_home: Path | None,
    timeout_seconds: float,
    label: str,
) -> subprocess.CompletedProcess[str]:
    try:
        result = subprocess.run(
            [*resolve_command_prefix(command_prefix), *arguments],
            cwd=cwd,
            env=_environment(codex_home),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            shell=False,
            timeout=timeout_seconds,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired) as error:
        raise CodexEnvironmentError(f"Codex {label} could not complete") from error
    if result.returncode != 0:
        raise CodexEnvironmentError(
            f"Codex {label} failed with exit code {result.returncode}"
        )
    return result


def _json_output(result: subprocess.CompletedProcess[str], label: str) -> Any:
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError as error:
        raise CodexEnvironmentError(f"Codex {label} returned invalid JSON") from error


def _prompt_measurement(result: subprocess.CompletedProcess[str]) -> tuple[int, int]:
    value = _json_output(result, "prompt inspection")
    if isinstance(value, list):
        item_count = len(value)
    elif isinstance(value, dict) and isinstance(value.get("items"), list):
        item_count = len(value["items"])
    else:
        raise CodexEnvironmentError("Codex prompt inspection returned an invalid item list")
    return item_count, len(result.stdout.encode("utf-8"))


def _find_unsupported_schema_keywords(value: Any) -> set[str]:
    found: set[str] = set()
    if isinstance(value, Mapping):
        found.update(UNSUPPORTED_STRUCTURED_OUTPUT_KEYWORDS & set(value))
        for child in value.values():
            found.update(_find_unsupported_schema_keywords(child))
    elif isinstance(value, list):
        for child in value:
            found.update(_find_unsupported_schema_keywords(child))
    return found


def run_codex_preflight(
    *,
    policy: CodexEnvironmentPolicy,
    command_prefix: tuple[str, ...],
    source_codex_home: Path,
    clean_codex_home: Path,
    workspace: Path,
    model: str,
    rates: UsageRates,
    prompt: str,
    today: date | None = None,
) -> dict[str, Any]:
    """Inspect local state only; this function never executes a model turn."""

    current_date = today or date.today()
    try:
        effective_date = date.fromisoformat(rates.effective_date)
    except ValueError as error:
        raise CodexEnvironmentError("rate effective date is not an ISO date") from error
    rate_age = (current_date - effective_date).days
    if rate_age < 0:
        raise CodexEnvironmentError("rate card effective date is in the future")
    if rate_age > policy.maximum_rate_age_days:
        raise CodexEnvironmentError("rate card is older than the preflight policy permits")
    if rates.model != model:
        raise CodexEnvironmentError("rate-card model does not match the configured model")

    unsupported = _find_unsupported_schema_keywords(SUBMISSION_SCHEMA)
    if unsupported:
        raise CodexEnvironmentError(
            "structured-output schema uses unsupported keywords: "
            + ", ".join(sorted(unsupported))
        )

    version_result = _run_codex(
        command_prefix,
        ("--version",),
        cwd=workspace,
        codex_home=clean_codex_home,
        timeout_seconds=policy.preflight_timeout_seconds,
        label="version check",
    )
    version_match = VERSION_PATTERN.search(version_result.stdout + version_result.stderr)
    if not version_match:
        raise CodexEnvironmentError("Codex version output was not recognized")
    installed_version = tuple(int(part) for part in version_match.groups())
    if installed_version < policy.minimum_codex_version:
        raise CodexEnvironmentError("installed Codex CLI is older than the policy minimum")

    login = _run_codex(
        command_prefix,
        ("login", "status"),
        cwd=workspace,
        codex_home=clean_codex_home,
        timeout_seconds=policy.preflight_timeout_seconds,
        label="authentication check",
    )
    if "Logged in using ChatGPT" not in login.stdout + login.stderr:
        raise CodexEnvironmentError("Codex is not authenticated with ChatGPT")

    models = _json_output(
        _run_codex(
            command_prefix,
            ("debug", "models"),
            cwd=workspace,
            codex_home=clean_codex_home,
            timeout_seconds=policy.preflight_timeout_seconds,
            label="model catalog check",
        ),
        "model catalog",
    )
    model_items = models.get("models") if isinstance(models, dict) else models
    if not isinstance(model_items, list):
        raise CodexEnvironmentError("Codex model catalog has an invalid shape")
    model_names = {
        item.get("slug") or item.get("model") or item.get("id")
        for item in model_items
        if isinstance(item, Mapping)
    }
    if model not in model_names:
        raise CodexEnvironmentError("configured model is absent from the Codex catalog")

    plugins = _json_output(
        _run_codex(
            command_prefix,
            ("plugin", "list", "--json"),
            cwd=workspace,
            codex_home=clean_codex_home,
            timeout_seconds=policy.preflight_timeout_seconds,
            label="plugin check",
        ),
        "plugin list",
    )
    installed_plugins = plugins.get("installed") if isinstance(plugins, dict) else None
    if not isinstance(installed_plugins, list):
        raise CodexEnvironmentError("Codex plugin list has an invalid shape")
    enabled_plugins = [
        item for item in installed_plugins if isinstance(item, Mapping) and item.get("enabled")
    ]
    if enabled_plugins:
        raise CodexEnvironmentError("temporary Codex home still has enabled plugins")

    mcp_servers = _json_output(
        _run_codex(
            command_prefix,
            ("mcp", "list", "--json"),
            cwd=workspace,
            codex_home=clean_codex_home,
            timeout_seconds=policy.preflight_timeout_seconds,
            label="MCP check",
        ),
        "MCP list",
    )
    if not isinstance(mcp_servers, list):
        raise CodexEnvironmentError("Codex MCP list has an invalid shape")
    enabled_mcps = [
        item for item in mcp_servers if isinstance(item, Mapping) and item.get("enabled")
    ]
    if enabled_mcps:
        raise CodexEnvironmentError("temporary Codex home still has enabled MCP servers")

    clean_prompt_result = _run_codex(
        command_prefix,
        ("debug", "prompt-input", prompt),
        cwd=workspace,
        codex_home=clean_codex_home,
        timeout_seconds=policy.preflight_timeout_seconds,
        label="prompt inspection",
    )
    prompt_items, prompt_bytes = _prompt_measurement(clean_prompt_result)
    if prompt_bytes > policy.maximum_prompt_json_bytes:
        raise CodexEnvironmentError("model-visible prompt exceeds the preflight byte budget")

    baseline_bytes: int | None = None
    if policy.measure_baseline_prompt:
        try:
            baseline = _run_codex(
                command_prefix,
                ("debug", "prompt-input", prompt),
                cwd=workspace,
                codex_home=source_codex_home,
                timeout_seconds=policy.preflight_timeout_seconds,
                label="baseline prompt inspection",
            )
            _, baseline_bytes = _prompt_measurement(baseline)
        except CodexEnvironmentError:
            baseline_bytes = None

    reduction = baseline_bytes - prompt_bytes if baseline_bytes is not None else None
    reduction_percent = (
        round(reduction * 100 / baseline_bytes, 2)
        if baseline_bytes not in (None, 0) and reduction is not None
        else None
    )
    return {
        "version": 1,
        "status": "passed",
        "isolation": "temporary-codex-home",
        "codex_version": ".".join(str(part) for part in installed_version),
        "authentication": "chatgpt",
        "model": model,
        "model_available": True,
        "rate_effective_date": rates.effective_date,
        "rate_age_days": rate_age,
        "structured_output_schema": "compatible",
        "enabled_plugin_count": 0,
        "enabled_mcp_count": 0,
        "prompt_item_count": prompt_items,
        "prompt_json_bytes": prompt_bytes,
        "maximum_prompt_json_bytes": policy.maximum_prompt_json_bytes,
        "baseline_prompt_json_bytes": baseline_bytes,
        "prompt_json_byte_reduction": reduction,
        "prompt_json_byte_reduction_percent": reduction_percent,
        "model_call_performed": False,
    }
