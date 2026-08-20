"""In-memory product catalog with deterministic lookups."""

from __future__ import annotations

from collections.abc import Iterable
from decimal import Decimal

from .errors import UnknownProductError
from .models import OrderLine, Product, normalize_sku


class Catalog:
    """Store products by normalized SKU."""

    def __init__(self, products: Iterable[Product] = ()) -> None:
        self._products: dict[str, Product] = {}
        for product in products:
            self.add(product)

    def add(self, product: Product) -> None:
        if not isinstance(product, Product):
            raise TypeError("catalog values must be Product records")
        if product.sku in self._products:
            raise ValueError(f"duplicate SKU: {product.sku}")
        self._products[product.sku] = product

    def replace(self, product: Product) -> None:
        if product.sku not in self._products:
            raise UnknownProductError(product.sku)
        self._products[product.sku] = product

    def get(self, sku: str) -> Product:
        normalized = normalize_sku(sku)
        try:
            return self._products[normalized]
        except KeyError as error:
            raise UnknownProductError(normalized) from error

    def contains(self, sku: str) -> bool:
        try:
            self.get(sku)
        except UnknownProductError:
            return False
        return True

    def active_products(self) -> tuple[Product, ...]:
        return tuple(
            product
            for product in sorted(self._products.values(), key=lambda item: item.sku)
            if product.active
        )

    def require_active(self, sku: str) -> Product:
        product = self.get(sku)
        if not product.active:
            raise UnknownProductError(f"inactive SKU: {product.sku}")
        return product

    def line_value(self, line: OrderLine) -> Decimal:
        product = self.require_active(line.sku)
        return product.unit_price * line.quantity

    def order_value(self, lines: Iterable[OrderLine]) -> Decimal:
        total = sum((self.line_value(line) for line in lines), Decimal("0.00"))
        return total.quantize(Decimal("0.01"))

    def line_weight(self, line: OrderLine) -> int:
        product = self.require_active(line.sku)
        return product.weight_grams * line.quantity

    def snapshot(self) -> tuple[dict[str, object], ...]:
        return tuple(
            {
                "sku": product.sku,
                "name": product.name,
                "unit_price": str(product.unit_price),
                "weight_grams": product.weight_grams,
                "active": product.active,
            }
            for product in sorted(self._products.values(), key=lambda item: item.sku)
        )

    def __len__(self) -> int:
        return len(self._products)
