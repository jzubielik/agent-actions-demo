-- Percentage discounts. percent is a whole number from 1 to 100.
CREATE TABLE discount_codes (
    code TEXT PRIMARY KEY,
    percent INTEGER NOT NULL CHECK (percent BETWEEN 1 AND 100),
    active INTEGER NOT NULL DEFAULT 1 CHECK (active IN (0, 1))
);
