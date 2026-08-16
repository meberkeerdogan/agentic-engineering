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
inventory = workspace / "inventory.py"
reporting = workspace / "reporting.py"
roadmap = workspace / "roadmap.py"
progress = workspace / "progress.py"
if calculator.is_file():
    source = calculator.read_text(encoding="utf-8")
    source = source.replace(
        "    return ordered[middle]\n",
        "    if len(ordered) % 2:\n"
        "        return ordered[middle]\n"
        "    return (ordered[middle - 1] + ordered[middle]) / 2\n",
    )
    calculator.write_text(source, encoding="utf-8")
    task_id = "median-fix"
    summary = "fixed the bounded median fixture"
    artifact_refs = ["calculator.py"]
    changed_paths = [calculator]
    test_command = "python -m unittest -v test_calculator.py"
elif inventory.is_file() and reporting.is_file():
    with inventory.open("a", encoding="utf-8") as stream:
        stream.write(
            "\n\ndef low_stock_skus(items: list[dict], threshold: int = 5) -> list[str]:\n"
            "    if threshold < 0:\n"
            "        raise ValueError('threshold must be non-negative')\n"
            "    return sorted(normalize_sku(item['sku']) for item in items "
            "if item['quantity'] <= threshold)\n"
        )
    with reporting.open("a", encoding="utf-8") as stream:
        stream.write(
            "\n\ndef format_restock_report(items: list[dict], threshold: int = 5) -> str:\n"
            "    from inventory import low_stock_skus\n"
            "    skus = low_stock_skus(items, threshold)\n"
            "    return 'Restock: ' + (', '.join(skus) if skus else 'none')\n"
        )
    task_id = "restock-report"
    summary = "implemented the multi-file restock report"
    artifact_refs = ["inventory.py", "reporting.py"]
    changed_paths = [inventory, reporting]
    test_command = "python -m unittest -v test_restock.py test_existing.py"
elif roadmap.is_file() and progress.is_file():
    with roadmap.open("a", encoding="utf-8") as stream:
        stream.write(
            "\n\ndef ready_item_ids(items: list[dict]) -> list[str]:\n"
            "    completed = set(completed_item_ids(items))\n"
            "    return sorted(item['id'] for item in items if item['status'] == "
            "'pending' and set(item['depends_on']) <= completed)\n"
            "\n\ndef blocking_dependencies(items: list[dict]) -> dict[str, list[str]]:\n"
            "    completed = set(completed_item_ids(items))\n"
            "    return {item['id']: sorted(set(item['depends_on']) - completed) "
            "for item in items if item['status'] == 'pending' and "
            "set(item['depends_on']) - completed}\n"
        )
    with progress.open("a", encoding="utf-8") as stream:
        stream.write(
            "\n\ndef build_progress_summary(items: list[dict]) -> dict:\n"
            "    from roadmap import blocking_dependencies, ready_item_ids\n"
            "    total = len(items)\n"
            "    completed = completed_count(items)\n"
            "    return {'total': total, 'completed': completed, "
            "'completion_ratio': round(completed / total, 2) if total else 0.0, "
            "'ready': ready_item_ids(items), "
            "'blocked': blocking_dependencies(items)}\n"
        )
    task_id = "roadmap-evolution"
    summary = "implemented dependency-aware roadmap progress"
    artifact_refs = ["roadmap.py", "progress.py"]
    changed_paths = [roadmap, progress]
    test_command = "python -m unittest -v test_evolution.py test_existing.py"
else:
    raise SystemExit("unsupported offline live fixture")
output_path.write_text(
    json.dumps(
        {
            "claimed_complete": True,
            "summary": summary,
            "artifact_refs": artifact_refs,
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
                "command": test_command,
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
                "id": "change-workspace",
                "type": "file_change",
                "changes": [
                    {"path": str(path), "kind": "update"} for path in changed_paths
                ],
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
                "command": test_command,
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
            "prompt_received": task_id in prompt,
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
