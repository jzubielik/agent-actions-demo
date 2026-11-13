---
name: money-review
description: Checklist for code that computes, rounds, converts or formats an amount of money. Use it when a diff touches pricing, discounts, VAT, invoices or the display of an amount.
---

1. **No floats.** Find every `float`, `/` on amounts, `round()`, `toFixed`, `parseFloat` and `Number` arithmetic on amounts in the diff. An amount is an integer in minor units or a `Decimal`. A float in one step is enough for a wrong cent: show an input where the result differs.
2. **Rounding.** It must be half up and explicit. Python's `round()` and `Decimal` default are half even.
3. **Where it rounds.** VAT is rounded once on the net amount of the invoice. Rounding per line and adding up gives a different total.
4. **Currency digits.** No division or multiplication by 100. JPY has no decimals, KWD has three.
5. **Sums.** After the change, do the lines, the discount and the total still add up? `build_invoice` refuses an order that does not.
6. **Tests.** A change of an amount has a test with a value that rounds (a half), not only round numbers.

Mark each finding with the prefix `[money]`.
