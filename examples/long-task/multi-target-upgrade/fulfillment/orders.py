"""Order validation, aggregation, and allocation."""

from __future__ import annotations

from collections import defaultdict
from collections.abc import Iterable

from .catalog import Catalog
from .errors import InsufficientStockError, InvalidOrderError
from .inventory import Inventory
from .models import Allocation, Order, OrderLine, normalize_sku


def aggregate_lines(lines: Iterable[OrderLine]) -> tuple[OrderLine, ...]:
    """Merge duplicate SKUs and return a stable tuple."""

    quantities: dict[str, int] = defaultdict(int)
    for line in lines:
        if not isinstance(line, OrderLine):
            raise InvalidOrderError("all lines must be OrderLine records")
        quantities[line.sku] += line.quantity
    return tuple(
        OrderLine(sku, quantities[sku])
        for sku in sorted(quantities)
    )


def validate_order(order: Order, catalog: Catalog) -> Order:
    """Return an order with aggregated active catalog lines."""

    if not isinstance(order, Order):
        raise InvalidOrderError("order must be an Order record")
    normalized_lines = aggregate_lines(order.lines)
    for line in normalized_lines:
        catalog.require_active(line.sku)
    return Order(order.order_id, order.destination_zone, normalized_lines)


def requested_quantities(order: Order) -> dict[str, int]:
    return {line.sku: line.quantity for line in aggregate_lines(order.lines)}


def allocation_quantities(
    allocations: Iterable[Allocation],
) -> dict[str, int]:
    totals: dict[str, int] = defaultdict(int)
    for allocation in allocations:
        if not isinstance(allocation, Allocation):
            raise TypeError("allocations must contain Allocation records")
        totals[allocation.sku] += allocation.quantity
    return dict(sorted(totals.items()))


def unallocated_quantities(
    order: Order,
    allocations: Iterable[Allocation],
) -> dict[str, int]:
    requested = requested_quantities(order)
    allocated = allocation_quantities(allocations)
    return {
        sku: quantity - allocated.get(sku, 0)
        for sku, quantity in requested.items()
        if quantity - allocated.get(sku, 0) > 0
    }


def allocations_by_warehouse(
    allocations: Iterable[Allocation],
) -> dict[str, tuple[Allocation, ...]]:
    grouped: dict[str, list[Allocation]] = defaultdict(list)
    for allocation in allocations:
        grouped[allocation.warehouse_id].append(allocation)
    return {
        warehouse_id: tuple(
            sorted(records, key=lambda item: (item.sku, item.quantity))
        )
        for warehouse_id, records in sorted(grouped.items())
    }


def require_fully_allocated(
    order: Order,
    allocations: Iterable[Allocation],
) -> tuple[Allocation, ...]:
    result = tuple(allocations)
    missing = unallocated_quantities(order, result)
    if missing:
        detail = ", ".join(f"{sku}={quantity}" for sku, quantity in missing.items())
        raise InsufficientStockError(f"order cannot be fully allocated: {detail}")
    return result


def allocate_order(
    order: Order,
    catalog: Catalog,
    inventory: Inventory,
) -> tuple[Allocation, ...]:
    """Allocate and reserve every line, splitting only when required."""

    raise NotImplementedError("multi-target upgrade: split order allocation")


def allocation_key(allocation: Allocation) -> tuple[str, str, int]:
    return (
        allocation.warehouse_id,
        normalize_sku(allocation.sku),
        allocation.quantity,
    )
