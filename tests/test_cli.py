import json
from pathlib import Path

from agentic_engineering import cli
from agentic_engineering import ui


def summary(verified: bool = True) -> dict:
    return {
        "verified_complete": verified,
        "run_id": "cli-001",
        "status": "verified" if verified else "rejected",
    }


def test_run_command_uses_shared_product_interface(
    tmp_path: Path, monkeypatch, capsys
) -> None:
    config = tmp_path / "product.json"
    config.write_text("{}\n", encoding="utf-8")
    received = {}

    def fake_run(project_root, config_path, run_id, *, confirm_paid_run):
        received.update(
            project_root=project_root,
            config_path=config_path,
            run_id=run_id,
            confirm_paid_run=confirm_paid_run,
        )
        return summary()

    monkeypatch.setattr(cli, "run_verified_workflow", fake_run)

    exit_code = cli.main(
        [
            "run",
            str(config),
            "--run-id",
            "cli-001",
            "--project-root",
            str(tmp_path),
            "--confirm-paid-run",
        ]
    )

    assert exit_code == 0
    assert received == {
        "project_root": tmp_path,
        "config_path": config,
        "run_id": "cli-001",
        "confirm_paid_run": True,
    }
    assert json.loads(capsys.readouterr().out)["status"] == "verified"


def test_run_command_returns_nonzero_when_evidence_rejects(
    tmp_path: Path, monkeypatch
) -> None:
    config = tmp_path / "product.json"
    config.write_text("{}\n", encoding="utf-8")
    monkeypatch.setattr(
        cli, "run_verified_workflow", lambda *args, **kwargs: summary(False)
    )

    assert cli.main(["run", str(config), "--run-id", "cli-001"]) == 1


def test_ui_command_starts_local_interface(tmp_path: Path, monkeypatch) -> None:
    received = {}

    def fake_serve(project_root, *, host, port, open_browser):
        received.update(
            project_root=project_root,
            host=host,
            port=port,
            open_browser=open_browser,
        )
        return 0

    monkeypatch.setattr(ui, "serve_ui", fake_serve)

    assert cli.main(["ui", "--project-root", str(tmp_path), "--no-open"]) == 0
    assert received == {
        "project_root": tmp_path,
        "host": "127.0.0.1",
        "port": 8765,
        "open_browser": False,
    }
