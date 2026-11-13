---
name: api-contract-review
description: Checklist for a change of the orders API or its contract. Use it when a pull request touches services/orders/orders/models.py, services/orders/orders/app.py or contracts/.
---

Check each point against the diff and the files it names. Report only what you confirmed in the code.

1. **Contract in step.** `contracts/orders.openapi.yaml` must change in the same pull request as the models or routes it describes. The CI job `contract` fails with "differs from the service" when it does not.
2. **Consumers.** For every response field the diff removes, renames or retypes, look it up in `contracts/consumers.yaml`. For each consumer listed, open the code that reads it (`services/billing/billing/`, `services/web/src/`) and say what breaks, with file and line. A field no consumer lists can go.
3. **New values.** A new value of `Status`, or of any enum in a response, reaches clients that switch on it. Check `STATUS_LABELS` in `services/web/src/orderSummary.ts` and the status checks in `services/billing/billing/invoice.py`.
4. **Requests.** A new required request field or parameter breaks existing callers. An optional one with a default does not.
5. **Generated types.** A contract change needs `services/web/src/generated/orders.ts` regenerated; the CI job `web` checks it.
6. **CI.** When the `contract` or `billing` job failed, quote the line of its log that names the field.

Mark each finding with the prefix `[contract]`.
