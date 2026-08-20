# Milestone 3: Allocate across warehouses

Implement `allocate_order(order, catalog, inventory)` using the ranked-source behavior from Milestone 1.

- Validate and aggregate the order.
- Split only when one warehouse cannot provide the full line.
- Preserve deterministic SKU and source order.
- Reserve only after every line can be filled.
- On shortage, raise `InsufficientStockError` and leave all stock unchanged.
