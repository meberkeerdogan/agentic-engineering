"""Run named unittest suites with stable machine-readable output."""

from __future__ import annotations

import json
import sys
import unittest
from collections.abc import Sequence


def main(arguments: Sequence[str] | None = None) -> int:
    names = list(sys.argv[1:] if arguments is None else arguments)
    if not names:
        raise SystemExit("at least one test name is required")
    loader = unittest.defaultTestLoader
    suite = unittest.TestSuite(loader.loadTestsFromName(name) for name in names)
    result = unittest.TestResult()
    suite.run(result)
    print(
        json.dumps(
            {
                "tests_run": result.testsRun,
                "failures": len(result.failures),
                "errors": len(result.errors),
                "skipped": len(result.skipped),
                "successful": result.wasSuccessful(),
            },
            sort_keys=True,
        )
    )
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    raise SystemExit(main())
