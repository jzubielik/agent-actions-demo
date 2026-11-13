# web

- The types of the API come from `src/generated/orders.ts` (`npm run gen`). No hand-written copy of a response shape, and no `any`.
- An amount is shown through `formatMinor`. It is never divided or multiplied by a power of ten in a component.
- `strict` stays on, with `noUncheckedIndexedAccess`.
