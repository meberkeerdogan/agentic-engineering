# Active specification: restock report

Add a small restocking feature across the existing inventory and reporting modules.

Requirements:

- Add `low_stock_skus(items, threshold=5)` to `inventory.py`.
- Each item is a mapping with `sku`, `quantity`, and `unit_price` fields.
- Return normalized SKUs whose quantity is less than or equal to the threshold, sorted alphabetically.
- Reject a negative threshold with `ValueError` and do not mutate the input.
- Add `format_restock_report(items, threshold=5)` to `reporting.py`.
- Return `Restock: SKU-1, SKU-2` for matching items and `Restock: none` when no item matches.
- Preserve all existing inventory value and formatting behavior.

Use only the Python standard library and run all unit tests.
