-- The list endpoint filters by customer and status and returns the newest first.
CREATE INDEX orders_customer_status_created ON orders (customer_id, status, created_at DESC);
