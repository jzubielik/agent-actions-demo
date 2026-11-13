# billing

- Billing reads orders only through `OrdersClient`, and only the fields listed for it in `contracts/consumers.yaml`.
- An invoice is built only for a paid order, and only when its lines and discount add up to the order's total.
- VAT is rounded once, on the net amount of the invoice, not per line.
