from __future__ import annotations

import http.client
import json
import threading
from contextlib import contextmanager
from pathlib import Path

import pytest

from agentic_engineering.ui import UiError, create_ui_server


@contextmanager
def running_server(project_root: Path, runner):
    server = create_ui_server(project_root, port=0, runner=runner)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield server
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)


def request(server, method: str, path: str, body=None, headers=None):
    host, port = server.server_address[:2]
    connection = http.client.HTTPConnection(host, port, timeout=5)
    payload = None if body is None else json.dumps(body)
    connection.request(method, path, body=payload, headers=headers or {})
    response = connection.getresponse()
    content = response.read()
    response_headers = dict(response.getheaders())
    connection.close()
    return response.status, response_headers, content


@pytest.fixture
def project(tmp_path: Path) -> Path:
    config = tmp_path / "examples" / "product-run.json"
    config.parent.mkdir()
    config.write_text("{}\n", encoding="utf-8")
    return tmp_path


def test_serves_local_page_with_security_headers(project: Path) -> None:
    with running_server(project, lambda *args, **kwargs: {}) as server:
        status, headers, body = request(server, "GET", "/")

    assert status == 200
    assert b"Agentic Engineering" in body
    assert b"Experimental features stay off" in body
    assert "default-src 'self'" in headers["Content-Security-Policy"]
    assert headers["X-Frame-Options"] == "DENY"
    assert headers["Cache-Control"] == "no-store"


def test_run_requires_session_token_and_paid_confirmation(project: Path) -> None:
    with running_server(project, lambda *args, **kwargs: {}) as server:
        status, _, _ = request(
            server,
            "POST",
            "/api/run",
            {"config": "examples/product-run.json", "run_id": "test", "confirm_paid_run": True},
            {"Content-Type": "application/json"},
        )
        assert status == 403

        _, _, session_body = request(server, "GET", "/api/session")
        token = json.loads(session_body)["token"]
        status, _, body = request(
            server,
            "POST",
            "/api/run",
            {"config": "examples/product-run.json", "run_id": "test", "confirm_paid_run": False},
            {"Content-Type": "application/json", "X-Agentic-Token": token},
        )

    assert status == 400
    assert "confirm" in json.loads(body)["error"]


def test_run_calls_the_shared_product_interface(project: Path) -> None:
    captured = {}
    summary = {
        "run_id": "ui-test",
        "status": "verified",
        "verified_complete": True,
        "regressions": [],
    }

    def fake_runner(project_root, config_path, run_id, *, confirm_paid_run):
        captured.update(
            project_root=project_root,
            config_path=config_path,
            run_id=run_id,
            confirm_paid_run=confirm_paid_run,
        )
        return summary

    with running_server(project, fake_runner) as server:
        _, _, session_body = request(server, "GET", "/api/session")
        token = json.loads(session_body)["token"]
        status, _, body = request(
            server,
            "POST",
            "/api/run",
            {"config": "examples/product-run.json", "run_id": "ui-test", "confirm_paid_run": True},
            {"Content-Type": "application/json", "X-Agentic-Token": token},
        )

    assert status == 200
    assert json.loads(body) == summary
    assert captured == {
        "project_root": project.resolve(),
        "config_path": (project / "examples" / "product-run.json").resolve(),
        "run_id": "ui-test",
        "confirm_paid_run": True,
    }


def test_run_rejects_config_path_outside_project(project: Path) -> None:
    with running_server(project, lambda *args, **kwargs: {}) as server:
        _, _, session_body = request(server, "GET", "/api/session")
        token = json.loads(session_body)["token"]
        status, _, body = request(
            server,
            "POST",
            "/api/run",
            {"config": "../outside.json", "run_id": "test", "confirm_paid_run": True},
            {"Content-Type": "application/json", "X-Agentic-Token": token},
        )

    assert status == 400
    assert "inside" in json.loads(body)["error"]


def test_server_refuses_non_loopback_binding(project: Path) -> None:
    with pytest.raises(UiError, match="only to this computer"):
        create_ui_server(project, host="0.0.0.0")


def test_ui_javascript_uses_safe_text_rendering() -> None:
    script = (
        Path(__file__).parents[1]
        / "agentic_engineering"
        / "ui_assets"
        / "app.js"
    ).read_text(encoding="utf-8")

    assert "textContent" in script
    assert "replaceChildren" in script
    assert "innerHTML" not in script
    assert "insertAdjacentHTML" not in script
