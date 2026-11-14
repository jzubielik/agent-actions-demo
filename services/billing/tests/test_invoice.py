from decimal import Decimal

import pytest

from billing.client import OrdersError
from billing.invoice import InvoiceError, build_invoice, major

VAT = Decimal("0.23")


def test_an_invoice_has_the_lines_and_amounts_of_the_order(orders, paid_order):
    invoice = build_invoice(orders.get_order(paid_order()), VAT)
    assert [(line.sku, line.quantity, line.unit_price, line.amount) for line in invoice.lines] == [
        ("book", 2, Decimal("12.50"), Decimal("25.00")),
        ("pen", 3, Decimal("1.99"), Decimal("5.97")),
    ]
    assert (invoice.discount, invoice.net) == (Decimal("0.00"), Decimal("30.97"))
    # 23% of 30.97 is 7.1231
    assert (invoice.vat, invoice.gross) == (Decimal("7.12"), Decimal("38.09"))
    assert (invoice.customer_id, invoice.currency) == ("c-1", "EUR")


def test_a_discount_is_taken_off_before_vat(orders, paid_order):
    invoice = build_invoice(orders.get_order(paid_order(discount_code="SPRING10")), VAT)
    assert (invoice.discount, invoice.net) == (Decimal("3.10"), Decimal("27.87"))
    # 23% of 27.87 is 6.4101
    assert invoice.vat == Decimal("6.41")


def test_a_currency_without_decimals_keeps_whole_amounts(orders, paid_order):
    order_id = paid_order(currency="JPY", items=[{"sku": "book", "quantity": 1, "unit_price_minor": 1500}])
    invoice = build_invoice(orders.get_order(order_id), Decimal("0.10"))
    assert (invoice.net, invoice.vat, invoice.gross) == (Decimal("1500"), Decimal("150"), Decimal("1650"))


def test_only_a_paid_order_is_invoiced(api, orders):
    body = {"customer_id": "c-1", "currency": "EUR", "items": [{"sku": "book", "quantity": 1, "unit_price_minor": 100}]}
    order_id = api.post("/orders", json=body).json()["id"]
    with pytest.raises(InvoiceError, match="only a paid order"):
        build_invoice(orders.get_order(order_id), VAT)


def test_a_cancelled_order_is_not_invoiced(api, orders):
    body = {"customer_id": "c-1", "currency": "EUR", "items": [{"sku": "book", "quantity": 1, "unit_price_minor": 100}]}
    order_id = api.post("/orders", json=body).json()["id"]
    api.post(f"/orders/{order_id}/place")
    api.post(f"/orders/{order_id}/cancel")
    with pytest.raises(InvoiceError, match="is cancelled"):
        build_invoice(orders.get_order(order_id), VAT)
    assert orders.paid_orders("c-1") == []


def test_an_order_that_does_not_add_up_is_not_invoiced(orders, paid_order):
    order = orders.get_order(paid_order())
    with pytest.raises(InvoiceError, match="do not add up"):
        build_invoice({**order, "subtotal_minor": order["subtotal_minor"] - 1}, VAT)


def test_an_order_whose_total_is_above_its_subtotal_is_not_invoiced(orders, paid_order):
    order = orders.get_order(paid_order())
    with pytest.raises(InvoiceError, match="do not add up"):
        build_invoice({**order, "total_minor": order["subtotal_minor"] + 1}, VAT)


def test_an_order_without_a_discount_code_whose_total_is_below_its_subtotal_is_not_invoiced(orders, paid_order):
    order = orders.get_order(paid_order())
    assert order["discount_code"] is None
    with pytest.raises(InvoiceError, match="do not add up"):
        build_invoice({**order, "total_minor": order["total_minor"] - 1}, VAT)


def test_paid_orders_of_a_customer_are_listed(orders, paid_order):
    first, second = paid_order(), paid_order()
    assert {order["id"] for order in orders.paid_orders("c-1")} == {first, second}
    assert orders.paid_orders("c-2") == []


def test_a_missing_order_is_an_error_of_its_own(orders):
    with pytest.raises(OrdersError, match="not found"):
        orders.get_order("missing")


def test_minor_units_become_the_major_unit_of_the_currency():
    assert major(1250, "EUR") == Decimal("12.50")
    assert major(1250, "JPY") == Decimal("1250")
    assert major(1250, "KWD") == Decimal("1.250")
