import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

# Billing is tested against the real orders service, started in this process.
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "orders"))

from orders.app import create_app  # noqa: E402

from billing.client import OrdersClient  # noqa: E402


@pytest.fixture
def api() -> TestClient:
    app = create_app(":memory:")
    app.state.conn.execute("INSERT INTO discount_codes (code, percent) VALUES ('SPRING10', 10)")
    return TestClient(app)


@pytest.fixture
def orders(api) -> OrdersClient:
    return OrdersClient(api)


@pytest.fixture
def paid_order(api):
    """Creates an order through the API and takes it to paid; returns its id."""

    def make(currency="EUR", discount_code=None, items=None) -> str:
        body = {
            "customer_id": "c-1",
            "currency": currency,
            "items": items or [{"sku": "book", "quantity": 2, "unit_price_minor": 1250}, {"sku": "pen", "quantity": 3, "unit_price_minor": 199}],
            "discount_code": discount_code,
        }
        order_id = api.post("/orders", json=body).json()["id"]
        api.post(f"/orders/{order_id}/place")
        api.post(f"/orders/{order_id}/pay")
        return order_id

    return make
