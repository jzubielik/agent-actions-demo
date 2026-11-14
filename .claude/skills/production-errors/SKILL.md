---
name: production-errors
description: Checks a change against the errors its service raises in production. Use it when a pull request changes code under services/orders, services/billing or services/web.
---

1. For each service the diff changes, call `mcp__prod_stats__recent_errors` once with its name (`orders`, `billing` or `web`).
2. For every error whose `where` names a function the diff changes, or a function that calls it, read that function and say which case it is: the change fixes the cause, the change leaves it as it is, or the change makes it more frequent. Give the error, its `count_24h` and its `first_seen`.
3. An error that started recently (`first_seen` within the last weeks) and is frequent is most likely caused by a recent change. When the diff touches its code and does not fix it, that is a finding.
4. A change that only hides an error (catches it, logs it and goes on, or drops the check that raises it) does not fix it. The check usually protects data: say what reaches the data without it.
5. An error in code the diff does not touch is not a finding.

Mark each finding with the prefix `[prod]`.
