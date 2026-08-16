"""Offline Codex double that fixes the deterministic live-pilot fixture."""

from __future__ import annotations

import json
import sys
from pathlib import Path


arguments = sys.argv[1:]
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
