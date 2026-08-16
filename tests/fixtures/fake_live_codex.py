"""Offline Codex double that fixes the deterministic live-pilot fixture."""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path


arguments = sys.argv[1:]
if arguments == ["--version"]:
    print(f"codex-cli {os.environ.get('FAKE_CODEX_VERSION', '0.147.0')}")
    raise SystemExit(0)
if arguments == ["exec", "--help"]:
    help_text = "Usage: codex exec [OPTIONS]"
    if os.environ.get("FAKE_CODEX_AUTO_REVIEW", "supported") == "supported":
        help_text += "\n\n  --approve-for-me"
    print(help_text)
    raise SystemExit(0)
if arguments == ["login", "status"]:
    if os.environ.get("FAKE_CODEX_AUTH", "chatgpt") == "chatgpt":
        print("Logged in using ChatGPT", file=sys.stderr)
        raise SystemExit(0)
    print("Not logged in", file=sys.stderr)
    raise SystemExit(1)
if arguments == ["debug", "models"]:
    model = os.environ.get("FAKE_CODEX_MODEL", "gpt-5.6-luna")
    print(json.dumps({"models": [{"slug": model}]}))
    raise SystemExit(0)
if arguments == ["plugin", "list", "--json"]:
    print(json.dumps({"installed": [], "available": []}))
    raise SystemExit(0)
if arguments == ["mcp", "list", "--json"]:
    print("[]")
    raise SystemExit(0)
if arguments[:2] == ["debug", "prompt-input"]:
    codex_home = Path(os.environ.get("CODEX_HOME", ""))
    clean = codex_home.name.startswith("agentic-engineering-")
    padding = "x" * (100 if clean else 3000)
    print(json.dumps([{"role": "developer", "content": padding}, {"role": "user", "content": arguments[-1]}]))
    raise SystemExit(0)

workspace = Path(arguments[arguments.index("-C") + 1])
output_path = Path(arguments[arguments.index("--output-last-message") + 1])
prompt = sys.stdin.read()
calculator = workspace / "calculator.py"
source = calculator.read_text(encoding="utf-8")
source = source.replace(
    "    return ordered[middle]\n",
    "    if len(ordered) % 2:\n"
    "        return ordered[middle]\n"
    "    return (ordered[middle - 1] + ordered[middle]) / 2\n",
)
calculator.write_text(source, encoding="utf-8")
output_path.write_text(
    json.dumps(
        {
            "claimed_complete": True,
            "summary": "fixed the bounded median fixture",
            "artifact_refs": ["calculator.py"],
        }
    ),
    encoding="utf-8",
)
print(json.dumps({"type": "thread.started", "thread_id": "offline-pilot"}))
print(
    json.dumps(
        {
            "type": "item.completed",
            "item": {
                "id": "command-reproduce",
                "type": "command_execution",
                "command": "python -m unittest -v test_calculator.py",
                "aggregated_output": "simulated initial failure",
                "exit_code": 1,
                "status": "failed",
            },
        }
    )
)
print(
    json.dumps(
        {
            "type": "item.completed",
            "item": {
                "id": "change-calculator",
                "type": "file_change",
                "changes": [{"path": str(calculator), "kind": "update"}],
                "status": "completed",
            },
        }
    )
)
print(
    json.dumps(
        {
            "type": "item.completed",
            "item": {
                "id": "command-validate",
                "type": "command_execution",
                "command": "python -m unittest -v test_calculator.py",
                "aggregated_output": "simulated passing tests",
                "exit_code": 0,
                "status": "completed",
            },
        }
    )
)
print(
    json.dumps(
        {
            "type": "item.completed",
            "item": {"type": "agent_message", "text": "fixture complete"},
            "prompt_received": "median-fix" in prompt,
        }
    )
)
print(
    json.dumps(
        {
            "type": "turn.completed",
            "usage": {
                "input_tokens": 1000,
                "cached_input_tokens": 200,
                "output_tokens": 100,
                "reasoning_output_tokens": 20,
            },
        }
    )
)
