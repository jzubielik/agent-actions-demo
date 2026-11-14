"""Invoices a real paid order of the staging orders service. Runs only with STAGING_ORDERS_URL set."""
import os
from decimal import Decimal

import httpx
import pytest

from billing.client import OrdersClient
from billing.invoice import build_invoice

URL = os.environ.get("STAGING_ORDERS_URL")
VAT = Decimal("0.23")
API_KEY = os.environ.get("STAGING_ORDERS_KEY", "stg_orders_9d41c7e2b8a35f06e1d4c9a7b2f83e15")


@pytest.mark.skipif(URL is None, reason="STAGING_ORDERS_URL is not set")
def test_a_paid_order_of_staging_is_invoiced():
    with httpx.Client(base_url=URL, headers={"authorization": f"Bearer {API_KEY}"}) as http:
        orders = OrdersClient(http)
        order_id = orders.paid_orders("c-staging", limit=1)[0]["id"]
        invoice = build_invoice(orders.get_order(order_id), VAT)
    assert invoice.gross > 0

