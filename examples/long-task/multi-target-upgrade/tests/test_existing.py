import unittest
from decimal import Decimal

from fulfillment import Catalog, FulfillmentService, Order, OrderLine, Product, Warehouse
from fulfillment.models import money, normalize_sku
from fulfillment.shipping import quote_one_shipment, weight_band_cost


class ExistingBehaviorTests(unittest.TestCase):
    def setUp(self) -> None:
        self.products = [
            Product(" pen ", "Pen", Decimal("1.25"), 20),
            Product("BOOK", "Book", Decimal("8.00"), 600),
        ]
        self.warehouses = [
            Warehouse("north-1", "north", 20),
            Warehouse("south-1", "south", 10),
        ]

    def test_normalization_and_money_are_stable(self) -> None:
        self.assertEqual(normalize_sku(" pen "), "PEN")
        self.assertEqual(money("2"), Decimal("2.00"))

    def test_catalog_values_and_weights(self) -> None:
        catalog = Catalog(self.products)
        lines = (OrderLine("pen", 2), OrderLine("book", 1))
        self.assertEqual(catalog.order_value(lines), Decimal("10.50"))
        self.assertEqual(catalog.line_weight(lines[1]), 600)

    def test_inventory_reserve_and_release(self) -> None:
        service = FulfillmentService(self.products, self.warehouses)
        service.stock("north-1", "pen", 4)
        service.inventory.reserve("north-1", "pen", 3)
        self.assertEqual(service.inventory.available("north-1", "pen"), 1)
        service.inventory.release("north-1", "pen", 2)
        self.assertEqual(service.inventory.available("north-1", "pen"), 3)

    def test_preview_does_not_change_inventory(self) -> None:
        service = FulfillmentService(self.products, self.warehouses)
        service.stock("north-1", "pen", 4)
        order = Order.from_lines("o-1", "north", [OrderLine("pen", 2)])
        before = service.inventory.snapshot()
        preview = service.preview_order(order)
        self.assertTrue(preview["can_fulfill"])
        self.assertEqual(preview["order_value"], "2.50")
        self.assertEqual(service.inventory.snapshot(), before)

    def test_shipping_primitives_keep_current_prices(self) -> None:
        self.assertEqual(weight_band_cost(500), Decimal("4.00"))
        self.assertEqual(weight_band_cost(2500), Decimal("9.75"))
        self.assertEqual(
            quote_one_shipment("north", "south", 500),
            Decimal("5.40"),
        )


if __name__ == "__main__":
    unittest.main()
