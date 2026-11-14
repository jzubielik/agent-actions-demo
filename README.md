# agent-actions demo

A small order system that uses [agent-actions](https://github.com/jzubielik/agent-actions) on its pull requests: an AI review with a merge gate, and the `/agent` command. The system is real enough to break in the ways real systems do: three services, one API contract between them, database migrations and a CI that checks each of these.

To see it at work, open the [example pull requests](#example-pull-requests).

## The system

| Part | What it is |
|---|---|
| `services/orders` | The orders API (Python, FastAPI, SQLite): create, read, list, place, pay and cancel an order, with discount codes |
| `services/billing` | Builds invoices from paid orders (Python). It reads orders through the API and is tested against the real service |
| `services/web` | The API client and the view model of the order page (TypeScript), with types generated from the contract |
| `contracts/orders.openapi.yaml` | The API contract, generated from the service |
| `contracts/consumers.yaml` | Which service reads which response field |
| `migrations/` | The database schema, one SQL file per change |
| `tools/contract.py` | Checks of the contract: in step with the service, consumers read fields that exist, changes that break a client |
| `tools/prod_stats` | An MCP server with a snapshot of production numbers: table sizes and recent errors. The numbers are invented |

Amounts are integers in the minor unit of their currency from the database to the browser. Nothing in the system turns one into a float.

## Run it

```sh
pip install -r requirements.txt
make test     # everything CI runs
make run      # the orders API on http://127.0.0.1:8000, interactive page at /docs
```

After a change of the API, `make contract` writes the contract and the types of the web client, and `make check` verifies them.

## CI

The `Tests` workflow has three jobs:

- **orders, billing, tools** run the Python tests. The billing tests start the orders service in the same process, so a field that billing reads and orders no longer sends fails here.
- **contract** fails when the committed contract differs from what the service serves, or when `consumers.yaml` lists a field the contract does not have. It also prints, as warnings, the changes that break a client of the contract on the base branch.
- **web** checks that the generated types match the contract, type-checks and runs the tests.

## How agent-actions is set up here

Each piece is a file you can copy into your own repository.

| Piece | File | What it does |
|---|---|---|
| Review after CI | `.github/workflows/ai-review.yml` | Waits for `Tests`, then reviews the commit once, with the CI logs. `/review` in a comment starts one by hand |
| `/agent` | `.github/workflows/ai-agent.yml` | A comment `/agent <request>` changes the code or answers a question |
| Rules | `CLAUDE.md`, `services/*/AGENTS.md` | What the code must keep to: money, SQL, the contract, tests, secrets. A change that breaks one is a finding |
| Review instructions | `REVIEW.md` | Which skill and which subagent the review uses for which kind of change |
| Skills | `.claude/skills/` | Four checklists of this team: `api-contract-review`, `migration-review`, `money-review`, `production-errors` |
| Subagents | `.claude/agents/` | `migration-reviewer` reads production numbers, `contract-reviewer` reads the consumer registry and the CI logs, `web-reviewer` checks the TypeScript of the web client |
| MCP server | `tools/prod_stats`, named in `mcp_config` of `ai-review.yml` | Gives the review `table_stats` and `recent_errors`. It starts from the base branch and needs nothing installed |

All of these are read from the base branch of a pull request, so a pull request cannot change the rules it is judged by.

## Example pull requests

These pull requests stay open, each to show one case. Their descriptions, review comments and the budget comment show what the review and `/agent` did.

| Pull request | What it shows |
|---|---|
| [#4](https://github.com/jzubielik/agent-actions-demo/pull/4) Removes a response field that billing reads | `contract-reviewer` finds the reader in `consumers.yaml` and quotes the failing CI jobs. After two `/agent` fixes the review still asks for the field, with the production error rate from `prod_stats`. |
| [#6](https://github.com/jzubielik/agent-actions-demo/pull/6) An index on `orders` | `[migration]`: built in one statement on 48.2M rows, with the numbers from `table_stats`. |
| [#7](https://github.com/jzubielik/agent-actions-demo/pull/7) A column on `discount_codes` | The same kind of migration on 340 rows gets no lock finding. A `CHECK` that lets malformed dates in is found, and `/agent` fixes it. |
| [#8](https://github.com/jzubielik/agent-actions-demo/pull/8) `ORDER BY` from a fixed map in an f-string | No SQL injection finding, as the rule allows it. A test that could not fail is noted; after `/agent` fixes it, the review finds that sorting mixes currencies. |
| [#9](https://github.com/jzubielik/agent-actions-demo/pull/9) A discount percentage with a fraction | `[money]`: a float rounds an exact half down, with an input that shows the wrong cent. `/agent` moves it to `Decimal`. |
| [#10](https://github.com/jzubielik/agent-actions-demo/pull/10) The order history rows | `web-reviewer`: an `any` against the package rules, and a cast that hides a status with no badge. |
| [#12](https://github.com/jzubielik/agent-actions-demo/pull/12) When an order was paid | A field that nothing writes: every paid order returns `paid_at: null`. |
| [#13](https://github.com/jzubielik/agent-actions-demo/pull/13) An invoice tolerance of one cent | A change that hides a production error instead of fixing it, and an API key committed in a test. |
| [#17](https://github.com/jzubielik/agent-actions-demo/pull/17) The invoice email | The pull request loosens the money rule in `CLAUDE.md` for its own code. The review judges it by the rule on `main`; `/agent` fixes the code and leaves the rule to a person. |
| [#18](https://github.com/jzubielik/agent-actions-demo/pull/18) A pytest bump | A change with nothing to find: no findings, 5/5. |
