"""Inventory calculations used by the representative task pack."""


def normalize_sku(sku: str) -> str:
    """Return the canonical SKU representation."""

    return sku.strip().upper()


def inventory_value(items: list[dict]) -> float:
    """Return the total inventory value without mutating the items."""

    return sum(item["quantity"] * item["unit_price"] for item in items)
