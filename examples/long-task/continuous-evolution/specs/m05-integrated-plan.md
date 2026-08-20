# Milestone 5: Build the integrated plan

Implement `FulfillmentService.build_plan(order)` using the earlier allocation, shipping, and reporting milestones.

- Validate the order, allocate and reserve stock, and quote shipments.
- Return `status: ready` plus the stable order, allocation, shipping, and exception sections.
- Let validation and insufficient-stock errors propagate.
