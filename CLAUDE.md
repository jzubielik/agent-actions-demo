# Rules of this repository

Three services share one API contract: `services/orders` serves it, `services/billing` and `services/web` consume it.

## Money

- An amount is an integer in the minor unit of its currency (`*_minor`) or a `Decimal`. Never a `float`, in any service, also not for one step of a calculation.
- Rounding is half up, to the minor unit of the currency, and is written out (`ROUND_HALF_UP`).
- A currency does not always have two decimals. Use the helpers (`billing.invoice.major`, `web/src/money.ts`), not a division by 100.

## Database

- SQL takes its values as parameters. Text is put into a statement only when it comes from a fixed list in the code.
- A schema change is a new file in `migrations/`. A file that is on `main` is never edited.
- A write that touches more than one row or table is one transaction.

## API contract

- `contracts/orders.openapi.yaml` is generated from the service (`make contract`) and committed with the change.
- A response field that `contracts/consumers.yaml` lists for a consumer is not removed or retyped unless that consumer changes in the same pull request.
- A consumer that starts reading a field adds it to `contracts/consumers.yaml`.

## Tests

- A change of behaviour comes with a test that fails without it.
- Billing is tested against the real orders service (`services/billing/tests/conftest.py`), not against a hand-written copy of its responses.

## Secrets

- No credential, token or key in the repository, also not in tests or examples.
