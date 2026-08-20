# Milestone 2: Report allocation exceptions

Implement `fulfillment_exceptions(order, allocations)`.

- Return one record for every SKU that is not fully allocated, ordered by SKU.
- Each record contains `type`, `sku`, `requested`, `allocated`, and `missing`.
- Use the type value `unallocated`.
- Duplicate order lines count toward the same requested SKU total.
