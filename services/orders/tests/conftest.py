import pytest
from fastapi.testclient import TestClient

from orders.app import create_app


@pytest.fixture
def client() -> TestClient:
    app = create_app(":memory:")
    app.state.conn.execute("INSERT INTO discount_codes (code, percent) VALUES ('SPRING10', 10)")
    app.state.conn.execute("INSERT INTO discount_codes (code, percent, active) VALUES ('OLD50', 50, 0)")
    return TestClient(app)


@pytest.fixture
def new_order() -> dict:
    return {
        "customer_id": "c-1",
        "currency": "EUR",
        "items": [
            {"sku": "book", "quantity": 2, "unit_price_minor": 1250},
            {"sku": "pen", "quantity": 3, "unit_price_minor": 199},
        ],
    }
