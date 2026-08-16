import unittest

from progress import completed_count
from roadmap import completed_item_ids, item_ids


class ExistingRoadmapTests(unittest.TestCase):
    def setUp(self) -> None:
        self.items = [
            {"id": "spec", "status": "completed", "depends_on": []},
            {"id": "build", "status": "pending", "depends_on": ["spec"]},
        ]

    def test_item_ids_preserve_declared_order(self) -> None:
        self.assertEqual(item_ids(self.items), ["spec", "build"])

    def test_completed_helpers(self) -> None:
        self.assertEqual(completed_item_ids(self.items), ["spec"])
        self.assertEqual(completed_count(self.items), 1)


if __name__ == "__main__":
    unittest.main()
