"""Builds an invoice from a paid order. Amounts are Decimal in the major unit of the currency."""
from dataclasses import dataclass
from decimal import ROUND_HALF_UP, Decimal

# Digits after the decimal point, for currencies that do not have two.
EXPONENTS = {"JPY": 0, "KRW": 0, "BHD": 3, "KWD": 3}


class InvoiceError(Exception):
    pass


@dataclass(frozen=True)
class Line:
    sku: str
    quantity: int
    unit_price: Decimal
    amount: Decimal


@dataclass(frozen=True)
class Invoice:
    order_id: str
    customer_id: str
    currency: str
    lines: tuple[Line, ...]
    discount: Decimal
    net: Decimal
    vat: Decimal
    gross: Decimal


def major(minor: int, currency: str) -> Decimal:
    """An amount in minor units as a Decimal in the major unit, with the currency's digits."""
    return Decimal(minor).scaleb(-EXPONENTS.get(currency, 2))


def build_invoice(order: dict, vat_rate: Decimal) -> Invoice:
    """The invoice of a paid order. vat_rate is a fraction, for example Decimal("0.23")."""
    if order["status"] != "paid":
        raise InvoiceError(f"order {order['id']} is {order['status']}, only a paid order is invoiced")
    currency = order["currency"]
    lines = tuple(
        Line(
            sku=item["sku"],
            quantity=item["quantity"],
            unit_price=major(item["unit_price_minor"], currency),
            amount=major(item["quantity"] * item["unit_price_minor"], currency),
        )
        for item in order["items"]
    )
    subtotal = major(order["subtotal_minor"], currency)
    net = major(order["total_minor"], currency)
    # The discount is what the order takes off its subtotal.
    discount = subtotal - net
    # The order's total is what the customer paid; an invoice that adds up to something else
    # must not go out.
    if sum((line.amount for line in lines), Decimal(0)) != subtotal or discount < 0:
        raise InvoiceError(f"order {order['id']}: the lines and the discount do not add up to the total")
    cent = Decimal(1).scaleb(-EXPONENTS.get(currency, 2))
    vat = (net * vat_rate).quantize(cent, rounding=ROUND_HALF_UP)
    return Invoice(order["id"], order["customer_id"], currency, lines, discount, net, vat, net + vat)
