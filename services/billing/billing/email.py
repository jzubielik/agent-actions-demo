"""The text of the email that sends an invoice to the customer."""
from decimal import Decimal

from .invoice import Invoice


def _amount(value: Decimal, currency: str) -> str:
    # The invoice's Decimals already carry the currency's digits (see `major`), so they are
    # printed as they are: no float, no fixed precision.
    return f"{value:f} {currency}"


def invoice_email(invoice: Invoice) -> str:
    rows = [f"{line.quantity} x {line.sku}: {_amount(line.amount, invoice.currency)}" for line in invoice.lines]
    if invoice.discount:
        rows.append(f"Discount: -{_amount(invoice.discount, invoice.currency)}")
    rows += [
        f"Net: {_amount(invoice.net, invoice.currency)}",
        f"VAT: {_amount(invoice.vat, invoice.currency)}",
        f"Total: {_amount(invoice.gross, invoice.currency)}",
    ]
    return f"Invoice for order {invoice.order_id}\n\n" + "\n".join(rows) + "\n"
