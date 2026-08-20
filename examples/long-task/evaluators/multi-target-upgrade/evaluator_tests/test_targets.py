import unittest
from decimal import Decimal

from fulfillment import (
    Allocation,
    Catalog,
    FulfillmentService,
    InsufficientStockError,
    Inventory,
    Order,
    OrderLine,
    Product,
    Warehouse,
)
from fulfillment.orders import allocate_order
from fulfillment.reporting import fulfillment_exceptions
from fulfillment.shipping import quote_allocations


def products() -> list[Product]:
    return [
        Product("PEN", "Pen", Decimal("1.25"), 100),
        Product("BOOK", "Book", Decimal("8.00"), 800),
    ]


def warehouses() -> list[Warehouse]:
    return [
        Warehouse("north-b", "north", 20),
        Warehouse("south-a", "south", 5),
        Warehouse("north-a", "north", 10),
    ]


def stocked_inventory() -> Inventory:
    inventory = Inventory(warehouses())
    inventory.set_available("north-a", "PEN", 2)
    inventory.set_available("north-b", "PEN", 4)
    inventory.set_available("south-a", "PEN", 5)
    inventory.set_available("north-a", "BOOK", 1)
    inventory.set_available("south-a", "BOOK", 2)
    return inventory


class RankedSourcesTests(unittest.TestCase):
    def test_zone_then_priority_then_id_and_only_stocked(self) -> None:
        inventory = stocked_inventory()
        ranked = inventory.ranked_sources("pen", "north")
        self.assertEqual(
            [warehouse.warehouse_id for warehouse in ranked],
            ["north-a", "north-b", "south-a"],
        )
        self.assertEqual(inventory.ranked_sources("MISSING", "north"), ())


class SplitAllocationTests(unittest.TestCase):
    def test_splits_in_rank_order_and_reserves(self) -> None:
        inventory = stocked_inventory()
        catalog = Catalog(products())
        order = Order.from_lines("o-1", "north", [OrderLine("PEN", 5)])
        result = allocate_order(order, catalog, inventory)
        self.assertEqual(
            result,
            (
                Allocation("north-a", "PEN", 2),
                Allocation("north-b", "PEN", 3),
            ),
        )
        self.assertEqual(inventory.available("north-a", "PEN"), 0)
        self.assertEqual(inventory.available("north-b", "PEN"), 1)

    def test_shortage_is_atomic_across_multiple_skus(self) -> None:
        inventory = stocked_inventory()
        before = inventory.snapshot()
        order = Order.from_lines(
            "o-2",
            "north",
            [OrderLine("PEN", 3), OrderLine("BOOK", 9)],
        )
        with self.assertRaises(InsufficientStockError):
            allocate_order(order, Catalog(products()), inventory)
        self.assertEqual(inventory.snapshot(), before)


class ShippingQuoteTests(unittest.TestCase):
    def test_groups_allocations_by_warehouse(self) -> None:
        inventory = stocked_inventory()
        allocations = (
            Allocation("north-a", "PEN", 2),
            Allocation("south-a", "BOOK", 1),
            Allocation("north-a", "BOOK", 1),
        )
        quotes = quote_allocations(
            allocations,
            "north",
            Catalog(products()),
            inventory,
        )
        self.assertEqual([quote.warehouse_id for quote in quotes], ["north-a", "south-a"])
        self.assertEqual([quote.weight_grams for quote in quotes], [1000, 800])
        self.assertEqual([quote.amount for quote in quotes], [Decimal("7.50"), Decimal("10.12")])
        self.assertEqual(quote_allocations((), "north", Catalog(products()), inventory), ())


class ExceptionReportTests(unittest.TestCase):
    def test_reports_missing_units_in_sku_order(self) -> None:
        order = Order.from_lines(
            "o-3",
            "north",
            [OrderLine("PEN", 5), OrderLine("BOOK", 2)],
        )
        allocations = (Allocation("north-a", "PEN", 3),)
        self.assertEqual(
            fulfillment_exceptions(order, allocations),
            [
                {"type": "unallocated", "sku": "BOOK", "requested": 2, "allocated": 0, "missing": 2},
                {"type": "unallocated", "sku": "PEN", "requested": 5, "allocated": 3, "missing": 2},
            ],
        )


class IntegratedPlanTests(unittest.TestCase):
    def test_builds_complete_plan_and_reserves_stock(self) -> None:
        service = FulfillmentService(products(), warehouses())
        service.stock("north-a", "PEN", 2)
        service.stock("north-b", "PEN", 4)
        order = Order.from_lines("o-4", "north", [OrderLine("PEN", 5)])
        plan = service.build_plan(order)
        self.assertEqual(plan["status"], "ready")
        self.assertEqual(plan["order"]["order_id"], "o-4")
        self.assertEqual(plan["allocation"]["allocation_count"], 2)
        self.assertEqual(plan["shipping"]["shipment_count"], 2)
        self.assertEqual(plan["exceptions"], [])
        self.assertEqual(service.inventory.total_available("PEN"), 1)


if __name__ == "__main__":
    unittest.main()
