# Milestone 4: Quote split shipments

Implement `quote_allocations(...)`.

- Return one quote per source warehouse, ordered by warehouse ID.
- Combine allocations from the same warehouse before calculating weight.
- Use the existing product weights, warehouse zones, weight bands, and zone multipliers.
- Empty allocations return an empty tuple.
