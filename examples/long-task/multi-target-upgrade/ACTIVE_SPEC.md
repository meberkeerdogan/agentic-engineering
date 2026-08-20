# Fulfillment Upgrade

Upgrade the existing fulfillment library without breaking its current behavior. Keep the public data records and existing functions compatible.

## Target 1: Ranked warehouse sources

Implement `Inventory.ranked_sources(sku, destination_zone)`.

- Include only warehouses with at least one available unit of the SKU.
- Put warehouses in the destination zone first.
- Within each group, sort by lower numeric priority, then warehouse ID.
- Return an immutable tuple. Do not change stock.

## Target 2: Atomic split allocation

Implement `allocate_order(order, catalog, inventory)`.

- Validate and aggregate the order before allocation.
- Allocate each SKU from `ranked_sources`, splitting across warehouses only when one warehouse cannot supply the full quantity.
- Return allocations in SKU order and source-ranking order.
- Reserve stock only after every order line can be fully allocated.
- If any SKU is short, raise `InsufficientStockError` and leave all stock unchanged.

## Target 3: Split-shipment quotes

Implement `quote_allocations(...)`.

- Return one quote per warehouse, ordered by warehouse ID.
- Combine all allocations from the same warehouse before calculating weight.
- Use the existing catalog weights, warehouse zones, weight bands, and zone multipliers.
- Empty allocations return an empty tuple.

## Target 4: Exception report

Implement `fulfillment_exceptions(order, allocations)`.

- Return one record for each SKU that is not fully allocated, ordered by SKU.
- Each record contains `type`, `sku`, `requested`, `allocated`, and `missing`.
- Use the type value `unallocated`.
- Return an empty list when every requested unit is allocated.

## Target 5: Integrated plan

Implement `FulfillmentService.build_plan(order)`.

- Validate the order, allocate and reserve stock, and quote the resulting shipments.
- Return `status: ready` plus the existing stable order, allocation, shipping, and exception report sections.
- Let validation and insufficient-stock errors propagate.

## Verification

Run the visible regression suite with:

```powershell
python -m unittest discover -s tests
```

The independent evaluator also checks the five targets and additional protected behavior. Do not add network access or external dependencies.
