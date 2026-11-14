from decimal import Decimal

from billing.email import invoice_email
from billing.invoice import build_invoice

VAT = Decimal("0.23")


def test_the_email_lists_the_lines_and_the_amounts(orders, paid_order):
    text = invoice_email(build_invoice(orders.get_order(paid_order()), VAT))
    assert "2 x book: 25.00 EUR" in text
    assert "Total: 38.09 EUR" in text


def test_a_currency_without_decimals_is_shown_without_decimals(orders, paid_order):
    order_id = paid_order(currency="JPY", items=[{"sku": "book", "quantity": 1, "unit_price_minor": 1500}])
    text = invoice_email(build_invoice(orders.get_order(order_id), VAT))
    assert "1 x book: 1500 JPY" in text
    assert "VAT: 345 JPY" in text
    assert "Total: 1845 JPY" in text


def test_a_currency_with_three_decimals_keeps_all_of_them(orders, paid_order):
    # As a float, 1.255 is formatted with two decimals as 1.25.
    order_id = paid_order(currency="KWD", items=[{"sku": "book", "quantity": 1, "unit_price_minor": 1255}])
    text = invoice_email(build_invoice(orders.get_order(order_id), VAT))
    assert "1 x book: 1.255 KWD" in text
    assert "Net: 1.255 KWD" in text
    assert "VAT: 0.289 KWD" in text
    assert "Total: 1.544 KWD" in text
