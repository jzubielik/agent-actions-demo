"""Client of the orders API. The fields billing reads are listed in contracts/consumers.yaml."""
import httpx


class OrdersError(Exception):
    pass


class OrdersClient:
    def __init__(self, http: httpx.Client):
        self._http = http

    def get_order(self, order_id: str) -> dict:
        response = self._http.get(f"/orders/{order_id}")
        if response.status_code == 404:
            raise OrdersError(f"order {order_id} not found")
        response.raise_for_status()
        return response.json()

    def paid_orders(self, customer_id: str, limit: int = 100) -> list[dict]:
        response = self._http.get("/orders", params={"customer_id": customer_id, "status": "paid", "limit": limit})
        response.raise_for_status()
        return response.json()
