"""Offline `codex exec` double used by adapter tests."""

from __future__ import annotations

import json
import sys
from pathlib import Path


mode = "normal"
for argument in sys.argv[1:]:
    if argument.startswith("--fake-mode="):
        mode = argument.split("=", 1)[1]

prompt = sys.stdin.read()
arguments = sys.argv[1:]
output_index = arguments.index("--output-last-message") + 1
schema_index = arguments.index("--output-schema") + 1
output_path = Path(arguments[output_index])
schema_path = Path(arguments[schema_index])

print(
    json.dumps(
        {
            "prompt_from_stdin": "bounded agentic-engineering" in prompt,
            "prompt_in_argv": any("bounded agentic-engineering" in item for item in arguments),
            "schema_exists": schema_path.is_file(),
            "json_mode": "--json" in arguments,
        }
    )
)

if mode == "fail":
    print("simulated failure", file=sys.stderr)
    raise SystemExit(7)
if mode == "malformed":
    output_path.write_text("not-json", encoding="utf-8")
else:
    output_path.write_text(
        json.dumps(
            {
                "claimed_complete": True,
                "summary": "fake executor completed its bounded task",
                "artifact_refs": ["src/fake.py"],
            }
        ),
        encoding="utf-8",
    )
