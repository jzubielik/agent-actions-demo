import { expect, test } from "vitest";
import { ApiError, OrdersApi } from "../src/client";
import { order } from "./fixtures";

function fakeFetch(status: number, body: unknown) {
  const calls: { url: string; init: RequestInit | undefined }[] = [];
  const fetcher = async (url: string, init?: RequestInit) => {
    calls.push({ url, init });
    return new Response(typeof body === "string" ? body : JSON.stringify(body), { status });
  };
  return { calls, fetcher };
}

test("an order is read by its id, which is escaped in the path", async () => {
  const { calls, fetcher } = fakeFetch(200, order);
  expect(await new OrdersApi("https://api.test", fetcher).getOrder("a/b")).toEqual(order);
  expect(calls[0]?.url).toBe("https://api.test/orders/a%2Fb");
});

test("orders are listed for a customer, with the status only when given", async () => {
  const { calls, fetcher } = fakeFetch(200, [order]);
  const api = new OrdersApi("https://api.test", fetcher);
  await api.listOrders("c 1");
  await api.listOrders("c-1", "paid");
  expect(calls.map((call) => call.url)).toEqual([
    "https://api.test/orders?customer_id=c+1",
    "https://api.test/orders?customer_id=c-1&status=paid",
  ]);
});

test("a new order is sent as JSON", async () => {
  const { calls, fetcher } = fakeFetch(201, order);
  const body = { customer_id: "c-1", currency: "EUR", items: order.items };
  await new OrdersApi("https://api.test", fetcher).createOrder(body);
  expect(calls[0]?.init?.method).toBe("POST");
  expect(JSON.parse(String(calls[0]?.init?.body))).toEqual(body);
});

test("an order is cancelled with a POST to its cancel path", async () => {
  const { calls, fetcher } = fakeFetch(200, { ...order, status: "cancelled" });
  const cancelled = await new OrdersApi("https://api.test", fetcher).cancelOrder("o 1");
  expect(cancelled.status).toBe("cancelled");
  expect(calls[0]).toMatchObject({ url: "https://api.test/orders/o%201/cancel", init: { method: "POST" } });
});

test("an error carries the status and the detail of the API", async () => {
  const { fetcher } = fakeFetch(409, { detail: "an order that is paid cannot become placed" });
  const error = await new OrdersApi("https://api.test", fetcher).placeOrder("o-1").catch((e: unknown) => e);
  expect(error).toBeInstanceOf(ApiError);
  expect(error).toMatchObject({ status: 409, message: "an order that is paid cannot become placed" });
});

test("an error without a JSON body is reported by its status", async () => {
  const { fetcher } = fakeFetch(502, "<html>bad gateway</html>");
  await expect(new OrdersApi("https://api.test", fetcher).getOrder("o-1")).rejects.toMatchObject({
    status: 502,
    message: "request failed with status 502",
  });
});
