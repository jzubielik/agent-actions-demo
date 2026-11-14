from decimal import Decimal

from billing.email import invoice_email
from billing.invoice import build_invoice

VAT = Decimal("0.23")


def test_the_email_lists_the_lines_and_the_amounts(orders, paid_order):
    text = invoice_email(build_invoice(orders.get_order(paid_order()), VAT))
    assert "2 x book: 25.00 EUR" in text
    assert "Total: 38.09 EUR" in text
