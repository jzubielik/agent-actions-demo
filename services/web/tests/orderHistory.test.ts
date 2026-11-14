import { expect, test } from "vitest";
import { historyRows } from "../src/orderHistory";
import { order } from "./fixtures";

test("each order is a row with its badge, total and date", () => {
  expect(historyRows([order, { ...order, id: "o-2", status: "paid" }], "en-IE")).toEqual([
    { id: "o-1", badge: "grey", total: "€26.99", placed: "4 Mar 2026" },
    { id: "o-2", badge: "green", total: "€26.99", placed: "4 Mar 2026" },
  ]);
});
