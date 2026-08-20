"""Stable dictionaries intended for JSON reports."""

from __future__ import annotations

from collections.abc import Iterable
from decimal import Decimal

from .inventory import Inventory
from .models import Allocation, Order, ShippingQuote
from .orders import allocation_quantities, unallocated_quantities


def inventory_summary(inventory: Inventory) -> dict[str, object]:
    snapshot = inventory.snapshot()
    total_units = sum(
        quantity
        for warehouse in snapshot.values()
        for quantity in warehouse.values()
    )
    return {
        "warehouse_count": len(snapshot),
        "total_units": total_units,
        "warehouses": snapshot,
    }


def allocation_summary(
    allocations: Iterable[Allocation],
) -> dict[str, object]:
    records = tuple(allocations)
    return {
        "allocation_count": len(records),
        "warehouse_count": len({item.warehouse_id for item in records}),
        "quantities": allocation_quantities(records),
        "allocations": [
            {
                "warehouse_id": item.warehouse_id,
                "sku": item.sku,
                "quantity": item.quantity,
            }
            for item in sorted(
                records,
                key=lambda item: (item.warehouse_id, item.sku, item.quantity),
            )
        ],
    }


def quote_summary(quotes: Iterable[ShippingQuote]) -> dict[str, object]:
    records = tuple(quotes)
    total = sum((quote.amount for quote in records), Decimal("0.00"))
    return {
        "shipment_count": len(records),
        "shipping_total": str(total.quantize(Decimal("0.01"))),
        "quotes": [
            {
                "warehouse_id": quote.warehouse_id,
                "weight_grams": quote.weight_grams,
                "amount": str(quote.amount),
            }
            for quote in sorted(records, key=lambda item: item.warehouse_id)
        ],
    }


def fulfillment_exceptions(
    order: Order,
    allocations: Iterable[Allocation],
) -> list[dict[str, object]]:
    """Return stable exception records for every unallocated SKU."""

    raise NotImplementedError("multi-target upgrade: exception reporting")


def order_summary(order: Order) -> dict[str, object]:
    return {
        "order_id": order.order_id,
        "destination_zone": order.destination_zone,
        "line_count": len(order.lines),
        "requested_units": sum(line.quantity for line in order.lines),
    }
