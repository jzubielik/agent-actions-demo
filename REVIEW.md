# Instructions for the review

- For a change under `migrations/`, use the `migration-review` skill and ask the `migration-reviewer`.
- For a change of `services/orders/orders/models.py`, `services/orders/orders/app.py` or `contracts/`, use the `api-contract-review` skill and ask the `contract-reviewer`.
- For a change that computes, rounds, converts or formats an amount, use the `money-review` skill.
- For a change under `services/web/`, ask the `web-reviewer`.
- For a change of code under `services/`, the `rules-reviewer` runs the `production-errors` skill: it has the `prod_stats` tools, the main session does not. Do not run that skill in the main session, and do not report it as skipped.
- A skill gives its findings a prefix (`[contract]`, `[migration]`, `[money]`, `[prod]`). Keep it at the start of the finding's title, so the reader sees which checklist found it.
- If a pull request changes behaviour and has no test for it, say so in a note.
- The numbers of `tools/prod_stats` are a snapshot. Name the tool and the value when a finding rests on one.
