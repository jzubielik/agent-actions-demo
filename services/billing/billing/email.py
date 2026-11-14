"""The text of the email that sends an invoice to the customer."""
from .invoice import Invoice


def invoice_email(invoice: Invoice) -> str:
    rows = [f"{line.quantity} x {line.sku}: {float(line.amount):.2f} {invoice.currency}" for line in invoice.lines]
    if invoice.discount:
        rows.append(f"Discount: -{float(invoice.discount):.2f} {invoice.currency}")
    rows += [
        f"Net: {float(invoice.net):.2f} {invoice.currency}",
        f"VAT: {float(invoice.vat):.2f} {invoice.currency}",
        f"Total: {float(invoice.gross):.2f} {invoice.currency}",
    ]
    return f"Invoice for order {invoice.order_id}\n\n" + "\n".join(rows) + "\n"
