"""Small immutable records shared by the fulfillment modules."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from typing import Iterable

from .errors import InvalidOrderError


def normalize_sku(value: str) -> str:
    """Return one stable SKU representation."""

    if not isinstance(value, str):
        raise TypeError("SKU must be text")
    normalized = value.strip().upper()
    if not normalized:
        raise ValueError("SKU cannot be empty")
    if any(character.isspace() for character in normalized):
        raise ValueError("SKU cannot contain whitespace")
    return normalized


def normalize_identifier(value: str, label: str) -> str:
    """Validate user-facing identifiers without changing their case."""

    if not isinstance(value, str):
        raise TypeError(f"{label} must be text")
    normalized = value.strip()
    if not normalized:
        raise ValueError(f"{label} cannot be empty")
    return normalized


def money(value: Decimal | int | str) -> Decimal:
    """Convert a supported value into a non-negative two-decimal amount."""

    try:
        amount = value if isinstance(value, Decimal) else Decimal(str(value))
    except (InvalidOperation, ValueError) as error:
        raise ValueError("invalid money value") from error
    if not amount.is_finite() or amount < 0:
        raise ValueError("money value must be finite and non-negative")
    return amount.quantize(Decimal("0.01"))


@dataclass(frozen=True)
class Product:
    sku: str
    name: str
    unit_price: Decimal
    weight_grams: int
    active: bool = True

    def __post_init__(self) -> None:
        object.__setattr__(self, "sku", normalize_sku(self.sku))
        object.__setattr__(self, "name", normalize_identifier(self.name, "name"))
        object.__setattr__(self, "unit_price", money(self.unit_price))
        if isinstance(self.weight_grams, bool) or self.weight_grams <= 0:
            raise ValueError("weight must be a positive integer")


@dataclass(frozen=True)
class Warehouse:
    warehouse_id: str
    zone: str
    priority: int = 100

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "warehouse_id",
            normalize_identifier(self.warehouse_id, "warehouse ID"),
        )
        object.__setattr__(self, "zone", normalize_identifier(self.zone, "zone"))
        if isinstance(self.priority, bool) or not isinstance(self.priority, int):
            raise TypeError("priority must be an integer")


@dataclass(frozen=True)
class OrderLine:
    sku: str
    quantity: int

    def __post_init__(self) -> None:
        object.__setattr__(self, "sku", normalize_sku(self.sku))
        if isinstance(self.quantity, bool) or not isinstance(self.quantity, int):
            raise InvalidOrderError("quantity must be an integer")
        if self.quantity <= 0:
            raise InvalidOrderError("quantity must be positive")


@dataclass(frozen=True)
class Order:
    order_id: str
    destination_zone: str
    lines: tuple[OrderLine, ...]

    def __post_init__(self) -> None:
        object.__setattr__(
            self, "order_id", normalize_identifier(self.order_id, "order ID")
        )
        object.__setattr__(
            self,
            "destination_zone",
            normalize_identifier(self.destination_zone, "destination zone"),
        )
        if not self.lines:
            raise InvalidOrderError("order must contain at least one line")
        if not all(isinstance(line, OrderLine) for line in self.lines):
            raise InvalidOrderError("order lines must be OrderLine values")

    @classmethod
    def from_lines(
        cls,
        order_id: str,
        destination_zone: str,
        lines: Iterable[OrderLine],
    ) -> Order:
        return cls(order_id, destination_zone, tuple(lines))


@dataclass(frozen=True)
class Allocation:
    warehouse_id: str
    sku: str
    quantity: int

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "warehouse_id",
            normalize_identifier(self.warehouse_id, "warehouse ID"),
        )
        object.__setattr__(self, "sku", normalize_sku(self.sku))
        if isinstance(self.quantity, bool) or self.quantity <= 0:
            raise ValueError("allocation quantity must be positive")


@dataclass(frozen=True)
class ShippingQuote:
    warehouse_id: str
    weight_grams: int
    amount: Decimal

    def __post_init__(self) -> None:
        object.__setattr__(self, "amount", money(self.amount))
        if isinstance(self.weight_grams, bool) or self.weight_grams <= 0:
            raise ValueError("quote weight must be positive")
