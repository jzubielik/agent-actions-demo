-- Orders and their lines. Amounts are integers in the minor unit of the order's currency.
CREATE TABLE orders (
    id TEXT PRIMARY KEY,
    customer_id TEXT NOT NULL,
    currency TEXT NOT NULL CHECK (length(currency) = 3),
    status TEXT NOT NULL CHECK (status IN ('draft', 'placed', 'paid', 'cancelled')),
    discount_code TEXT,
    subtotal_minor INTEGER NOT NULL CHECK (subtotal_minor >= 0),
    discount_minor INTEGER NOT NULL CHECK (discount_minor >= 0),
    total_minor INTEGER NOT NULL CHECK (total_minor >= 0),
    created_at TEXT NOT NULL
);

CREATE TABLE order_items (
    order_id TEXT NOT NULL REFERENCES orders (id) ON DELETE CASCADE,
    position INTEGER NOT NULL,
    sku TEXT NOT NULL,
    quantity INTEGER NOT NULL CHECK (quantity > 0),
    unit_price_minor INTEGER NOT NULL CHECK (unit_price_minor >= 0),
    PRIMARY KEY (order_id, position)
);
