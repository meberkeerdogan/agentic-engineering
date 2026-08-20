"""Local browser interface for the supported verified workflow."""

from __future__ import annotations

import ipaddress
import json
import secrets
import threading
import webbrowser
from collections.abc import Callable, Mapping, Sequence
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from importlib.resources import files
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit

from .product import ProductRunError, WORKFLOW_ID, run_verified_workflow


class UiError(RuntimeError):
    """Raised when the local UI cannot be started safely."""


Runner = Callable[..., Mapping[str, Any]]

_ASSETS = {
    "/": ("index.html", "text/html; charset=utf-8"),
    "/assets/app.css": ("app.css", "text/css; charset=utf-8"),
    "/assets/app.js": ("app.js", "text/javascript; charset=utf-8"),
}


def _inside(root: Path, reference: str, *, suffix: str | None = None) -> Path:
    if not reference or Path(reference).is_absolute():
        raise UiError("use a project-relative path")
    candidate = (root / reference).resolve()
    try:
        candidate.relative_to(root)
    except ValueError as error:
        raise UiError("path must stay inside the project") from error
    if suffix and candidate.suffix.lower() != suffix:
        raise UiError(f"path must end in {suffix}")
    return candidate


def _safe_run_id(value: object) -> str:
    if not isinstance(value, str) or not value or len(value) > 80:
        raise UiError("run ID must contain 1 to 80 characters")
    allowed = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_")
    if any(character not in allowed for character in value):
        raise UiError("run ID may contain only letters, numbers, dashes, and underscores")
    return value


def _recent_runs(project_root: Path) -> list[dict[str, Any]]:
    run_root = project_root / ".agentic-runs"
    if not run_root.is_dir():
        return []
    recent: list[dict[str, Any]] = []
    for summary_path in sorted(
        run_root.glob("*/product-summary.json"),
        key=lambda path: path.stat().st_mtime,
        reverse=True,
    )[:10]:
        try:
            summary = json.loads(summary_path.read_text(encoding="utf-8"))
        except (OSError, UnicodeError, json.JSONDecodeError):
            continue
        if isinstance(summary, dict):
            recent.append(summary)
    return recent


class _UiState:
    def __init__(self, project_root: Path, runner: Runner) -> None:
        self.project_root = project_root.resolve()
        self.runner = runner
        self.token = secrets.token_urlsafe(32)
        self.run_lock = threading.Lock()


class _UiServer(ThreadingHTTPServer):
    ui_state: _UiState


class _Handler(BaseHTTPRequestHandler):
    server: _UiServer

    def log_message(self, format: str, *args: object) -> None:
        return

    @property
    def state(self) -> _UiState:
        return self.server.ui_state

    def _headers(self, content_type: str, length: int) -> None:
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(length))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("X-Frame-Options", "DENY")
        self.send_header("Referrer-Policy", "no-referrer")
        self.send_header(
            "Content-Security-Policy",
            "default-src 'self'; script-src 'self'; style-src 'self'; "
            "img-src 'self' data:; connect-src 'self'; frame-ancestors 'none'; "
            "base-uri 'none'; form-action 'self'",
        )

    def _send(self, status: HTTPStatus, body: bytes, content_type: str) -> None:
        self.send_response(status)
        self._headers(content_type, len(body))
        self.end_headers()
        self.wfile.write(body)

    def _json(self, status: HTTPStatus, value: object) -> None:
        body = json.dumps(value, ensure_ascii=False).encode("utf-8")
        self._send(status, body, "application/json; charset=utf-8")

    def _error(self, status: HTTPStatus, message: str) -> None:
        self._json(status, {"error": message})

    def do_GET(self) -> None:
        path = urlsplit(self.path).path
        if path == "/api/session":
            self._json(
                HTTPStatus.OK,
                {
                    "token": self.state.token,
                    "workflow_id": WORKFLOW_ID,
                    "project_name": self.state.project_root.name,
                    "project_root": str(self.state.project_root),
                    "default_config": "examples/product-run.json",
                    "recent_runs": _recent_runs(self.state.project_root),
                },
            )
            return
        asset = _ASSETS.get(path)
        if asset is None:
            self._error(HTTPStatus.NOT_FOUND, "not found")
            return
        name, content_type = asset
        body = files("agentic_engineering.ui_assets").joinpath(name).read_bytes()
        self._send(HTTPStatus.OK, body, content_type)

    def do_POST(self) -> None:
        if urlsplit(self.path).path != "/api/run":
            self._error(HTTPStatus.NOT_FOUND, "not found")
            return
        if self.headers.get("X-Agentic-Token") != self.state.token:
            self._error(HTTPStatus.FORBIDDEN, "invalid local session token")
            return
        try:
            length = int(self.headers.get("Content-Length", "0"))
        except ValueError:
            self._error(HTTPStatus.BAD_REQUEST, "invalid request length")
            return
        if length < 2 or length > 16_384:
            self._error(HTTPStatus.BAD_REQUEST, "invalid request size")
            return
        try:
            payload = json.loads(self.rfile.read(length).decode("utf-8"))
        except (UnicodeError, json.JSONDecodeError):
            self._error(HTTPStatus.BAD_REQUEST, "request must be valid JSON")
            return
        if not isinstance(payload, dict):
            self._error(HTTPStatus.BAD_REQUEST, "request must be a JSON object")
            return
        unexpected = set(payload) - {"config", "run_id", "confirm_paid_run"}
        if unexpected:
            self._error(HTTPStatus.BAD_REQUEST, "request contains unsupported fields")
            return
        if payload.get("confirm_paid_run") is not True:
            self._error(
                HTTPStatus.BAD_REQUEST,
                "confirm the paid authenticated run before starting",
            )
            return
        try:
            run_id = _safe_run_id(payload.get("run_id"))
            config_ref = payload.get("config")
            if not isinstance(config_ref, str):
                raise UiError("config must be a project-relative path")
            config_path = _inside(self.state.project_root, config_ref, suffix=".json")
            if not config_path.is_file():
                raise UiError("config file does not exist")
        except UiError as error:
            self._error(HTTPStatus.BAD_REQUEST, str(error))
            return
        if not self.state.run_lock.acquire(blocking=False):
            self._error(HTTPStatus.CONFLICT, "another run is already active")
            return
        try:
            summary = self.state.runner(
                self.state.project_root,
                config_path,
                run_id,
                confirm_paid_run=True,
            )
        except ProductRunError as error:
            self._error(HTTPStatus.BAD_REQUEST, str(error))
            return
        except Exception:
            self._error(HTTPStatus.INTERNAL_SERVER_ERROR, "the workflow failed unexpectedly")
            return
        finally:
            self.state.run_lock.release()
        self._json(HTTPStatus.OK, summary)


def create_ui_server(
    project_root: Path,
    *,
    host: str = "127.0.0.1",
    port: int = 8765,
    runner: Runner = run_verified_workflow,
) -> ThreadingHTTPServer:
    """Create a loopback-only server; callers control its lifetime."""

    try:
        address = ipaddress.ip_address(host)
    except ValueError as error:
        raise UiError("UI host must be a numeric loopback address") from error
    if address.version != 4 or not address.is_loopback:
        raise UiError("UI may bind only to this computer (127.0.0.1)")
    if not 0 <= port <= 65_535:
        raise UiError("port must be between 0 and 65535")
    server = _UiServer((host, port), _Handler)
    server.ui_state = _UiState(project_root, runner)
    return server


def serve_ui(
    project_root: Path,
    *,
    host: str = "127.0.0.1",
    port: int = 8765,
    open_browser: bool = True,
) -> int:
    """Serve the local UI until interrupted."""

    try:
        server = create_ui_server(project_root, host=host, port=port)
    except (OSError, UiError) as error:
        print(f"error: {error}")
        return 2
    bound_host, bound_port = server.server_address[:2]
    url = f"http://{bound_host}:{bound_port}/"
    print(f"Agentic Engineering UI: {url}")
    if open_browser:
        webbrowser.open(url)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
    return 0


def main(argv: Sequence[str] | None = None) -> int:
    import argparse

    parser = argparse.ArgumentParser(prog="python -m agentic_engineering.ui")
    parser.add_argument("--project-root", type=Path, default=Path.cwd())
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8765)
    parser.add_argument("--no-open", action="store_true")
    parsed = parser.parse_args(argv)
    return serve_ui(
        parsed.project_root,
        host=parsed.host,
        port=parsed.port,
        open_browser=not parsed.no_open,
    )


if __name__ == "__main__":
    raise SystemExit(main())
