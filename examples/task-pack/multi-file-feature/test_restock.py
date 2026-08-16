import unittest

from inventory import low_stock_skus
from reporting import format_restock_report


class RestockFeatureTests(unittest.TestCase):
    def setUp(self) -> None:
        self.items = [
            {"sku": " z-9 ", "quantity": 2, "unit_price": 3.5},
            {"sku": "a-1", "quantity": 5, "unit_price": 1.25},
            {"sku": "m-4", "quantity": 8, "unit_price": 2.0},
        ]

    def test_low_stock_skus_are_normalized_and_sorted(self) -> None:
        self.assertEqual(low_stock_skus(self.items), ["A-1", "Z-9"])

    def test_custom_threshold_and_empty_report(self) -> None:
        self.assertEqual(low_stock_skus(self.items, threshold=1), [])
        self.assertEqual(format_restock_report(self.items, threshold=1), "Restock: none")

    def test_report_uses_matching_skus(self) -> None:
        self.assertEqual(format_restock_report(self.items), "Restock: A-1, Z-9")

    def test_negative_threshold_is_rejected_without_mutation(self) -> None:
        before = [dict(item) for item in self.items]
        with self.assertRaises(ValueError):
            low_stock_skus(self.items, threshold=-1)
        self.assertEqual(self.items, before)


if __name__ == "__main__":
    unittest.main()
