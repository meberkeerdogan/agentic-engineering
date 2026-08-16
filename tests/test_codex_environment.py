from datetime import date
from pathlib import Path

import pytest

import agentic_engineering.codex_environment as environment_module
from agentic_engineering.codex_environment import (
    CodexEnvironmentError,
    CodexEnvironmentPolicy,
    TemporaryCodexHome,
    run_codex_preflight,
)
from agentic_engineering.codex_evidence import UsageRates


def policy_mapping() -> dict:
    return {
        "version": 1,
        "isolation": "temporary-codex-home",
        "authentication": "chatgpt",
        "minimum_codex_version": "0.147.0",
        "maximum_rate_age_days": 30,
        "maximum_prompt_json_bytes": 20000,
        "preflight_timeout_seconds": 60,
        "measure_baseline_prompt": True,
    }


def test_environment_policy_rejects_undeclared_fields() -> None:
    value = policy_mapping()
    value["surprise"] = True

    with pytest.raises(CodexEnvironmentError, match="exactly the version 1 fields"):
        CodexEnvironmentPolicy.from_mapping(value)


def test_temporary_codex_home_copies_auth_then_cleans_up(tmp_path: Path) -> None:
    source = tmp_path / "source-home"
    (source / "tmp").mkdir(parents=True)
    (source / "auth.json").write_text('{"fixture": true}\n', encoding="utf-8")

    temporary = TemporaryCodexHome(source)
    with temporary as clean_home:
        assert (clean_home / "auth.json").read_text("utf-8") == '{"fixture": true}\n'
        clean_path = clean_home

    assert not clean_path.exists()
    assert (source / "auth.json").is_file()


def test_preflight_rejects_known_unsupported_schema_before_cli(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(
        environment_module,
        "SUBMISSION_SCHEMA",
        {"type": "array", "uniqueItems": True},
    )
    rates = UsageRates(
        model="gpt-5.6-luna",
        unit="credits",
        effective_date="2026-08-16",
        source_url="https://example.test/rates",
        input_per_million=1,
        cached_input_per_million=1,
        output_per_million=1,
    )

    with pytest.raises(CodexEnvironmentError, match="uniqueItems"):
        run_codex_preflight(
            policy=CodexEnvironmentPolicy.from_mapping(policy_mapping()),
            command_prefix=("command-that-must-not-run",),
            source_codex_home=tmp_path,
            clean_codex_home=tmp_path,
            workspace=tmp_path,
            model="gpt-5.6-luna",
            rates=rates,
            prompt="bounded prompt",
            today=date(2026, 8, 16),
        )
