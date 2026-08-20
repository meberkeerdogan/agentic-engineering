"""Command-line interface for the supported Agentic Engineering product path."""

from __future__ import annotations

import argparse
import json
import sys
from collections.abc import Sequence
from pathlib import Path

from .active_spec import main as active_spec_main
from .product import ProductRunError, run_verified_workflow


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="agentic-engineering")
    subparsers = parser.add_subparsers(dest="command", required=True)

    run = subparsers.add_parser("run", help="run the frozen verified workflow")
    run.add_argument("config", type=Path)
    run.add_argument("--run-id", required=True)
    run.add_argument("--project-root", type=Path, default=Path.cwd())
    run.add_argument(
        "--confirm-paid-run",
        action="store_true",
        help="confirm that the authenticated Codex run may spend credits",
    )

    compile_parser = subparsers.add_parser(
        "compile", help="compile a specification revision history"
    )
    compile_parser.add_argument("history", type=Path)
    compile_parser.add_argument("--output", "-o", type=Path)
    compile_parser.add_argument("--behavior-only", action="store_true")
    compile_parser.add_argument("--fingerprint", action="store_true")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    arguments = list(sys.argv[1:] if argv is None else argv)
    if arguments and arguments[0] not in {"run", "compile", "-h", "--help"}:
        return active_spec_main(arguments)
    parsed = _parser().parse_args(arguments)
    if parsed.command == "compile":
        forwarded = [str(parsed.history)]
        if parsed.output:
            forwarded.extend(["--output", str(parsed.output)])
        if parsed.behavior_only:
            forwarded.append("--behavior-only")
        if parsed.fingerprint:
            forwarded.append("--fingerprint")
        return active_spec_main(forwarded)
    try:
        summary = run_verified_workflow(
            parsed.project_root,
            parsed.config,
            parsed.run_id,
            confirm_paid_run=parsed.confirm_paid_run,
        )
    except ProductRunError as error:
        print(f"error: {error}", file=sys.stderr)
        return 2
    json.dump(summary, sys.stdout, ensure_ascii=False, indent=2)
    sys.stdout.write("\n")
    return 0 if summary["verified_complete"] else 1
