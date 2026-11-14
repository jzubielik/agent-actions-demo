"""Amounts of an order. Everything is an integer in the minor unit of the currency."""


def subtotal(items: list[tuple[int, int]]) -> int:
    """items: (quantity, unit price in minor units) for each line."""
    return sum(quantity * unit_price for quantity, unit_price in items)


def discount(subtotal_minor: int, percent: float) -> int:
    """The discount for a percentage, which may have a fraction (2.5 for 2.5%), in minor units."""
    if not 0 <= percent <= 100:
        raise ValueError(f"percent must be between 0 and 100, got {percent}")
    # Half up: add a half and drop the fraction (the amount is never negative).
    return int(subtotal_minor * percent / 100 + 0.5)


def totals(items: list[tuple[int, int]], percent: float) -> tuple[int, int, int]:
    """(subtotal, discount, total). The total is never below zero."""
    before = subtotal(items)
    off = discount(before, percent)
    return before, off, before - off
