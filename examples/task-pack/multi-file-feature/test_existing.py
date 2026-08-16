import unittest

from inventory import inventory_value, normalize_sku
from reporting import format_inventory_value


class ExistingInventoryTests(unittest.TestCase):
    def setUp(self) -> None:
        self.items = [
            {"sku": " a-1 ", "quantity": 2, "unit_price": 3.5},
            {"sku": "b-2", "quantity": 4, "unit_price": 1.25},
        ]

    def test_normalize_sku(self) -> None:
        self.assertEqual(normalize_sku(" a-1 "), "A-1")

    def test_inventory_value_and_format(self) -> None:
        self.assertEqual(inventory_value(self.items), 12.0)
        self.assertEqual(format_inventory_value(self.items), "Inventory value: 12.00")

    def test_input_is_not_mutated(self) -> None:
        before = [dict(item) for item in self.items]
        inventory_value(self.items)
        self.assertEqual(self.items, before)


if __name__ == "__main__":
    unittest.main()
