"""Warehouse registration and stock accounting."""

from __future__ import annotations

from collections.abc import Iterable

from .errors import InsufficientStockError, UnknownWarehouseError
from .models import Warehouse, normalize_identifier, normalize_sku


class Inventory:
    """Track available units for registered warehouses."""

    def __init__(self, warehouses: Iterable[Warehouse] = ()) -> None:
        self._warehouses: dict[str, Warehouse] = {}
        self._stock: dict[tuple[str, str], int] = {}
        for warehouse in warehouses:
            self.register(warehouse)

    def register(self, warehouse: Warehouse) -> None:
        if not isinstance(warehouse, Warehouse):
            raise TypeError("warehouse must be a Warehouse record")
        if warehouse.warehouse_id in self._warehouses:
            raise ValueError(f"duplicate warehouse: {warehouse.warehouse_id}")
        self._warehouses[warehouse.warehouse_id] = warehouse

    def warehouse(self, warehouse_id: str) -> Warehouse:
        normalized = normalize_identifier(warehouse_id, "warehouse ID")
        try:
            return self._warehouses[normalized]
        except KeyError as error:
            raise UnknownWarehouseError(normalized) from error

    def warehouses(self) -> tuple[Warehouse, ...]:
        return tuple(
            sorted(
                self._warehouses.values(),
                key=lambda item: (item.priority, item.warehouse_id),
            )
        )

    def set_available(self, warehouse_id: str, sku: str, quantity: int) -> None:
        warehouse = self.warehouse(warehouse_id)
        normalized_sku = normalize_sku(sku)
        if isinstance(quantity, bool) or not isinstance(quantity, int):
            raise TypeError("quantity must be an integer")
        if quantity < 0:
            raise ValueError("quantity cannot be negative")
        self._stock[(warehouse.warehouse_id, normalized_sku)] = quantity

    def available(self, warehouse_id: str, sku: str) -> int:
        warehouse = self.warehouse(warehouse_id)
        return self._stock.get((warehouse.warehouse_id, normalize_sku(sku)), 0)

    def total_available(self, sku: str) -> int:
        normalized_sku = normalize_sku(sku)
        return sum(
            quantity
            for (warehouse_id, item_sku), quantity in self._stock.items()
            if warehouse_id in self._warehouses and item_sku == normalized_sku
        )

    def reserve(self, warehouse_id: str, sku: str, quantity: int) -> None:
        if isinstance(quantity, bool) or not isinstance(quantity, int) or quantity <= 0:
            raise ValueError("reservation quantity must be positive")
        current = self.available(warehouse_id, sku)
        if current < quantity:
            raise InsufficientStockError(
                f"requested {quantity} units but only {current} are available"
            )
        self.set_available(warehouse_id, sku, current - quantity)

    def release(self, warehouse_id: str, sku: str, quantity: int) -> None:
        if isinstance(quantity, bool) or not isinstance(quantity, int) or quantity <= 0:
            raise ValueError("release quantity must be positive")
        current = self.available(warehouse_id, sku)
        self.set_available(warehouse_id, sku, current + quantity)

    def low_stock(self, threshold: int) -> tuple[tuple[str, str, int], ...]:
        if isinstance(threshold, bool) or not isinstance(threshold, int):
            raise TypeError("threshold must be an integer")
        if threshold < 0:
            raise ValueError("threshold cannot be negative")
        return tuple(
            (warehouse_id, sku, quantity)
            for (warehouse_id, sku), quantity in sorted(self._stock.items())
            if quantity <= threshold
        )

    def snapshot(self) -> dict[str, dict[str, int]]:
        result: dict[str, dict[str, int]] = {
            warehouse_id: {} for warehouse_id in sorted(self._warehouses)
        }
        for (warehouse_id, sku), quantity in sorted(self._stock.items()):
            result[warehouse_id][sku] = quantity
        return result

    def ranked_sources(self, sku: str, destination_zone: str) -> tuple[Warehouse, ...]:
        """Return stocked warehouses in the required fulfillment order."""

        raise NotImplementedError("multi-target upgrade: ranked warehouse sources")
