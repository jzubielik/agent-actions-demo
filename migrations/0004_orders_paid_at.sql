-- When an order was paid, in UTC (ISO 8601). Null until it is paid.
ALTER TABLE orders ADD COLUMN paid_at TEXT;
