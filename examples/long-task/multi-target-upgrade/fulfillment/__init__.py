"""Public surface for the fulfillment example."""

from .catalog import Catalog
from .errors import (
    FulfillmentError,
    InsufficientStockError,
    InvalidOrderError,
    UnknownProductError,
    UnknownWarehouseError,
)
from .inventory import Inventory
from .models import Allocation, Order, OrderLine, Product, ShippingQuote, Warehouse
from .service import FulfillmentService

__all__ = [
    "Allocation",
    "Catalog",
    "FulfillmentError",
    "FulfillmentService",
    "InsufficientStockError",
    "InvalidOrderError",
    "Inventory",
    "Order",
    "OrderLine",
    "Product",
    "ShippingQuote",
    "UnknownProductError",
    "UnknownWarehouseError",
    "Warehouse",
]
