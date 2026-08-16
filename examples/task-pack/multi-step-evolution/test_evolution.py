import unittest

from progress import build_progress_summary
from roadmap import blocking_dependencies, ready_item_ids


class RoadmapEvolutionTests(unittest.TestCase):
    def setUp(self) -> None:
        self.items = [
            {"id": "spec", "status": "completed", "depends_on": []},
            {"id": "tests", "status": "pending", "depends_on": ["build"]},
            {"id": "docs", "status": "pending", "depends_on": ["spec"]},
            {"id": "build", "status": "pending", "depends_on": ["spec"]},
            {"id": "release", "status": "pending", "depends_on": ["tests", "docs"]},
        ]

    def test_ready_items_are_dependency_aware_and_sorted(self) -> None:
        self.assertEqual(ready_item_ids(self.items), ["build", "docs"])

    def test_blockers_exclude_ready_and_completed_items(self) -> None:
        self.assertEqual(
            blocking_dependencies(self.items),
            {"release": ["docs", "tests"], "tests": ["build"]},
        )

    def test_progress_summary_combines_all_steps(self) -> None:
        self.assertEqual(
            build_progress_summary(self.items),
            {
                "total": 5,
                "completed": 1,
                "completion_ratio": 0.2,
                "ready": ["build", "docs"],
                "blocked": {"release": ["docs", "tests"], "tests": ["build"]},
            },
        )

    def test_empty_summary_and_input_immutability(self) -> None:
        self.assertEqual(
            build_progress_summary([]),
            {
                "total": 0,
                "completed": 0,
                "completion_ratio": 0.0,
                "ready": [],
                "blocked": {},
            },
        )
        before = [
            {**item, "depends_on": list(item["depends_on"])} for item in self.items
        ]
        build_progress_summary(self.items)
        self.assertEqual(self.items, before)


if __name__ == "__main__":
    unittest.main()
