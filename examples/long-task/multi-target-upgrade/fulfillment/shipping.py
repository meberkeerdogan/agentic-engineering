"""Deterministic shipping price calculations."""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from decimal import Decimal

from .catalog import Catalog
from .inventory import Inventory
from .models import Allocation, ShippingQuote, money
from .orders import allocations_by_warehouse


DEFAULT_ZONE_MULTIPLIERS: dict[tuple[str, str], Decimal] = {
    ("north", "north"): Decimal("1.00"),
    ("north", "south"): Decimal("1.35"),
    ("south", "north"): Decimal("1.35"),
    ("south", "south"): Decimal("1.00"),
    ("central", "north"): Decimal("1.15"),
    ("central", "south"): Decimal("1.15"),
}


def weight_band_cost(weight_grams: int) -> Decimal:
    """Return a base parcel price for a positive weight."""

    if isinstance(weight_grams, bool) or not isinstance(weight_grams, int):
        raise TypeError("weight must be an integer")
    if weight_grams <= 0:
        raise ValueError("weight must be positive")
    if weight_grams <= 500:
        return Decimal("4.00")
    if weight_grams <= 2000:
        return Decimal("7.50")
    extra_kilos = (weight_grams - 2000 + 999) // 1000
    return Decimal("7.50") + Decimal(extra_kilos) * Decimal("2.25")


def zone_multiplier(
    source_zone: str,
    destination_zone: str,
    multipliers: Mapping[tuple[str, str], Decimal] = DEFAULT_ZONE_MULTIPLIERS,
) -> Decimal:
    source = source_zone.strip().lower()
    destination = destination_zone.strip().lower()
    if source == destination:
        return Decimal("1.00")
    try:
        return Decimal(multipliers[(source, destination)])
    except KeyError as error:
        raise ValueError(f"unsupported shipping route: {source} -> {destination}") from error


def shipment_weight(
    allocations: Iterable[Allocation],
    catalog: Catalog,
) -> int:
    total = 0
    for allocation in allocations:
        product = catalog.require_active(allocation.sku)
        total += product.weight_grams * allocation.quantity
    if total <= 0:
        raise ValueError("shipment must contain positive weight")
    return total


def quote_one_shipment(
    warehouse_zone: str,
    destination_zone: str,
    weight_grams: int,
) -> Decimal:
    return money(
        weight_band_cost(weight_grams)
        * zone_multiplier(warehouse_zone, destination_zone)
    )


def quote_allocations(
    allocations: Iterable[Allocation],
    destination_zone: str,
    catalog: Catalog,
    inventory: Inventory,
) -> tuple[ShippingQuote, ...]:
    """Return one deterministic quote per source warehouse."""

    raise NotImplementedError("multi-target upgrade: split shipping quotes")


def total_shipping(quotes: Iterable[ShippingQuote]) -> Decimal:
    return money(sum((quote.amount for quote in quotes), Decimal("0.00")))
