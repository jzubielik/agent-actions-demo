"""Amounts of an order. Everything is an integer in the minor unit of the currency."""
from decimal import ROUND_HALF_UP, Decimal


def subtotal(items: list[tuple[int, int]]) -> int:
    """items: (quantity, unit price in minor units) for each line."""
    return sum(quantity * unit_price for quantity, unit_price in items)


def discount(subtotal_minor: int, percent: Decimal | int) -> int:
    """The discount for a percentage, which may have a fraction (Decimal("2.5") for 2.5%),
    rounded half up to the minor unit."""
    percent = Decimal(str(percent))
    if not 0 <= percent <= 100:
        raise ValueError(f"percent must be between 0 and 100, got {percent}")
    exact = Decimal(subtotal_minor) * percent / Decimal(100)
    return int(exact.quantize(Decimal(1), rounding=ROUND_HALF_UP))


def totals(items: list[tuple[int, int]], percent: Decimal | int) -> tuple[int, int, int]:
    """(subtotal, discount, total). The total is never below zero."""
    before = subtotal(items)
    off = discount(before, percent)
    return before, off, before - off
