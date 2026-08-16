"""Human-readable inventory reports."""

from inventory import inventory_value


def format_inventory_value(items: list[dict]) -> str:
    """Format the total value with two decimal places."""

    return f"Inventory value: {inventory_value(items):.2f}"
