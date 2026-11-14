-- A discount code can end on a date. A code without one does not expire.
ALTER TABLE discount_codes ADD COLUMN expires_at TEXT CHECK (expires_at IS NULL OR expires_at = date(expires_at));
