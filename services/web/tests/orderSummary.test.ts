import { expect, test } from "vitest";
import { summarize } from "../src/orderSummary";
import { order } from "./fixtures";

test("a draft shows its lines, amounts and that it can be placed", () => {
  expect(summarize(order, "en-IE")).toEqual({
    status: "Draft",
    lines: [
      { label: "2 × book", amount: "€25.00" },
      { label: "pen", amount: "€1.99" },
    ],
    subtotal: "€26.99",
    total: "€26.99",
    placed: "4 Mar 2026",
    canPlace: true,
  });
});

test("a discount is shown as a negative amount", () => {
  const summary = summarize({ ...order, discount_code: "SPRING10", discount_minor: 270, total_minor: 2429 }, "en-IE");
  expect(summary.discount).toBe("-€2.70");
  expect(summary.total).toBe("€24.29");
});

test("only a draft can be placed", () => {
  expect(summarize({ ...order, status: "placed" }, "en-IE")).toMatchObject({ status: "Waiting for payment", canPlace: false });
  expect(summarize({ ...order, status: "paid" }, "en-IE").canPlace).toBe(false);
});
