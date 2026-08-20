# Milestone 1: Rank warehouse sources

Implement `Inventory.ranked_sources(sku, destination_zone)`.

- Include only warehouses with available stock for the SKU.
- Put warehouses in the destination zone first.
- Within each group, sort by lower numeric priority, then warehouse ID.
- Return a tuple and do not change stock.
