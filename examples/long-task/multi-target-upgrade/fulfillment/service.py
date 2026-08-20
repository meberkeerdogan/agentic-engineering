"""High-level fulfillment service assembled from focused modules."""

from __future__ import annotations

from collections.abc import Iterable

from .catalog import Catalog
from .inventory import Inventory
from .models import Order, Product, Warehouse
from .orders import allocate_order, validate_order
from .reporting import (
    allocation_summary,
    fulfillment_exceptions,
    order_summary,
    quote_summary,
)
from .shipping import quote_allocations


class FulfillmentService:
    """Own the catalog and inventory used for one planning session."""

    def __init__(
        self,
        products: Iterable[Product] = (),
        warehouses: Iterable[Warehouse] = (),
    ) -> None:
        self.catalog = Catalog(products)
        self.inventory = Inventory(warehouses)

    def stock(self, warehouse_id: str, sku: str, quantity: int) -> None:
        self.catalog.require_active(sku)
        self.inventory.set_available(warehouse_id, sku, quantity)

    def availability(self, sku: str) -> dict[str, int]:
        product = self.catalog.require_active(sku)
        return {
            warehouse.warehouse_id: self.inventory.available(
                warehouse.warehouse_id, product.sku
            )
            for warehouse in self.inventory.warehouses()
        }

    def can_fulfill(self, order: Order) -> bool:
        checked = validate_order(order, self.catalog)
        return all(
            self.inventory.total_available(line.sku) >= line.quantity
            for line in checked.lines
        )

    def status(self) -> dict[str, object]:
        return {
            "products": len(self.catalog),
            "warehouses": len(self.inventory.warehouses()),
            "stock": self.inventory.snapshot(),
        }

    def build_plan(self, order: Order) -> dict[str, object]:
        """Reserve stock and return the complete fulfillment plan."""

        raise NotImplementedError("multi-target upgrade: integrated plan")

    def preview_order(self, order: Order) -> dict[str, object]:
        checked = validate_order(order, self.catalog)
        return {
            **order_summary(checked),
            "order_value": str(self.catalog.order_value(checked.lines)),
            "can_fulfill": self.can_fulfill(checked),
        }


def build_plan_sections(
    order: Order,
    allocations: tuple,
    quotes: tuple,
) -> dict[str, object]:
    """Create the stable section layout used by the service result."""

    return {
        "order": order_summary(order),
        "allocation": allocation_summary(allocations),
        "shipping": quote_summary(quotes),
        "exceptions": fulfillment_exceptions(order, allocations),
    }
