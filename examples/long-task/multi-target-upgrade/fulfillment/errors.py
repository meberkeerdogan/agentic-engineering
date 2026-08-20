"""Domain errors for the fulfillment example."""


class FulfillmentError(ValueError):
    """Base error raised for invalid fulfillment operations."""


class UnknownProductError(FulfillmentError):
    """Raised when a SKU is not present in the catalog."""


class UnknownWarehouseError(FulfillmentError):
    """Raised when a warehouse identifier is not registered."""


class InsufficientStockError(FulfillmentError):
    """Raised when a reservation is larger than available stock."""


class InvalidOrderError(FulfillmentError):
    """Raised when an order cannot be accepted."""
