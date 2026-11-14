-- The daily sales report reads the orders of one day.
CREATE INDEX orders_created ON orders (created_at);
