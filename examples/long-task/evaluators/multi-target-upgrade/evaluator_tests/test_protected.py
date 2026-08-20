import unittest
from decimal import Decimal

from fulfillment import (
    Catalog,
    FulfillmentService,
    InsufficientStockError,
    Order,
    OrderLine,
    Product,
    UnknownProductError,
    Warehouse,
)


class ProtectedBehaviorTests(unittest.TestCase):
    def test_duplicate_catalog_items_still_fail(self) -> None:
        product = Product("PEN", "Pen", Decimal("1.00"), 10)
        with self.assertRaisesRegex(ValueError, "duplicate SKU"):
            Catalog([product, product])

    def test_unknown_and_inactive_products_still_fail(self) -> None:
        catalog = Catalog([Product("OLD", "Old", Decimal("1.00"), 10, active=False)])
        with self.assertRaises(UnknownProductError):
            catalog.require_active("OLD")
        with self.assertRaises(UnknownProductError):
            catalog.get("MISSING")

    def test_failed_direct_reservation_does_not_change_stock(self) -> None:
        service = FulfillmentService(
            [Product("PEN", "Pen", Decimal("1.00"), 10)],
            [Warehouse("w-1", "north")],
        )
        service.stock("w-1", "PEN", 2)
        with self.assertRaises(InsufficientStockError):
            service.inventory.reserve("w-1", "PEN", 3)
        self.assertEqual(service.inventory.available("w-1", "PEN"), 2)

    def test_duplicate_lines_still_aggregate_in_preview(self) -> None:
        service = FulfillmentService(
            [Product("PEN", "Pen", Decimal("1.25"), 10)],
            [Warehouse("w-1", "north")],
        )
        service.stock("w-1", "PEN", 5)
        order = Order.from_lines(
            "o-1",
            "north",
            [OrderLine("PEN", 1), OrderLine("pen", 2)],
        )
        preview = service.preview_order(order)
        self.assertEqual(preview["line_count"], 1)
        self.assertEqual(preview["requested_units"], 3)
        self.assertEqual(preview["order_value"], "3.75")


if __name__ == "__main__":
    unittest.main()
