// Client of the orders API. The types come from the contract; run `npm run gen` after it changes.
import type { components } from "./generated/orders";

export type Order = components["schemas"]["Order"];
export type NewOrder = components["schemas"]["NewOrder"];
export type Status = components["schemas"]["Status"];

export class ApiError extends Error {
  constructor(
    readonly status: number,
    detail: string,
  ) {
    super(detail);
    this.name = "ApiError";
  }
}

type Fetch = (input: string, init?: RequestInit) => Promise<Response>;

export class OrdersApi {
  constructor(
    private readonly baseUrl: string,
    private readonly fetcher: Fetch = fetch,
  ) {}

  getOrder(id: string): Promise<Order> {
    return this.request(`/orders/${encodeURIComponent(id)}`);
  }

  listOrders(customerId: string, status?: Status): Promise<Order[]> {
    const query = new URLSearchParams({ customer_id: customerId });
    if (status !== undefined) query.set("status", status);
    return this.request(`/orders?${query}`);
  }

  createOrder(order: NewOrder): Promise<Order> {
    return this.request("/orders", { method: "POST", headers: { "content-type": "application/json" }, body: JSON.stringify(order) });
  }

  placeOrder(id: string): Promise<Order> {
    return this.request(`/orders/${encodeURIComponent(id)}/place`, { method: "POST" });
  }

  cancelOrder(id: string): Promise<Order> {
    return this.request(`/orders/${encodeURIComponent(id)}/cancel`, { method: "POST" });
  }

  private async request<T>(path: string, init?: RequestInit): Promise<T> {
    const response = await this.fetcher(`${this.baseUrl}${path}`, init);
    if (!response.ok) throw new ApiError(response.status, await detailOf(response));
    return (await response.json()) as T;
  }
}

// The API answers an error with {"detail": ...}; anything else is reported by its status.
async function detailOf(response: Response): Promise<string> {
  try {
    const body: unknown = await response.json();
    if (typeof body === "object" && body !== null && "detail" in body && typeof body.detail === "string") return body.detail;
  } catch {
    // Not JSON: fall through to the status.
  }
  return `request failed with status ${response.status}`;
}
