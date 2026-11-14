from decimal import Decimal

import pytest

from orders import pricing


def test_subtotal_is_the_sum_of_the_lines():
    assert pricing.subtotal([(2, 1250), (3, 199)]) == 3097


def test_discount_rounds_half_up_to_the_minor_unit():
    # 10% of 3097 is 309.7; 15% of 30 is 4.5
    assert pricing.discount(3097, 10) == 310
    assert pricing.discount(30, 15) == 5


def test_totals_without_a_discount():
    assert pricing.totals([(1, 999)], 0) == (999, 0, 999)


def test_a_full_discount_leaves_nothing_to_pay():
    assert pricing.totals([(1, 999)], 100) == (999, 999, 0)


@pytest.mark.parametrize("percent", [-1, 101])
def test_a_percentage_outside_the_range_is_refused(percent):
    with pytest.raises(ValueError):
        pricing.discount(1000, percent)


def test_a_percentage_can_have_a_fraction():
    assert pricing.discount(1000, Decimal("2.5")) == 25
    assert pricing.discount(2000, Decimal("12.5")) == 250


def test_a_fractional_percentage_rounds_an_exact_half_up():
    # 2.3% of 1500 is exactly 34.5; in float arithmetic it is 34.49999999999999
    assert pricing.discount(1500, Decimal("2.3")) == 35


def test_totals_with_a_fractional_percentage():
    assert pricing.totals([(1, 1500)], Decimal("2.3")) == (1500, 35, 1465)
