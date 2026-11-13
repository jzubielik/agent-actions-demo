import type { Order } from "../src/client";

export const order: Order = {
  id: "o-1",
  customer_id: "c-1",
  currency: "EUR",
  status: "draft",
  items: [
    { sku: "book", quantity: 2, unit_price_minor: 1250 },
    { sku: "pen", quantity: 1, unit_price_minor: 199 },
  ],
  discount_code: null,
  subtotal_minor: 2699,
  discount_minor: 0,
  total_minor: 2699,
  created_at: "2026-03-04T10:15:00+00:00",
};
