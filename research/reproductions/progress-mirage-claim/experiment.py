"""Deterministic claim-versus-verification observation fixture."""

import json
from pathlib import Path


claim = json.loads(Path("claimed-complete.json").read_text("utf-8"))
evaluation = json.loads(Path("independent-evaluation.json").read_text("utf-8"))
print(
    json.dumps(
        {
            "claimed_complete": claim["claimed_complete"],
            "verified_complete": evaluation["verified_complete"],
            "divergence": claim["claimed_complete"]
            and not evaluation["verified_complete"],
        },
        sort_keys=True,
    )
)
