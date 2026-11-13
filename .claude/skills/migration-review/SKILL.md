---
name: migration-review
description: Checklist for a database migration. Use it when a pull request adds or changes a file under migrations/.
---

Check each point. Where a point depends on the size of a table, call `mcp__prod_stats__table_stats` for that table and give the numbers you got.

1. **New file only.** A migration that is on the base branch must not change. A new one has the next number.
2. **Lock.** A statement that rewrites or scans a whole table (a new `NOT NULL` column without a default, a new `CHECK`, a column type change, an index built in one statement) holds a lock for as long as the table is large. Compare the table's `rows` and `writes_per_minute` with its `largest_lock_tolerated_ms`. On a table with millions of rows and steady writes this is blocking; on a table of a few hundred rows it is fine. Say which case it is and why.
3. **Safe order for a large table.** Add the column as nullable, backfill in batches, then add the constraint. A migration that does it in one step on a large table should be split.
4. **Existing rows.** A new constraint must hold for the rows that exist. Say what happens to rows that break it.
5. **Code in step.** The code that reads or writes the new column is in the same pull request, or the column has a default the old code can live with.
6. **One transaction.** The runner wraps each file in a transaction; a statement that cannot run in one needs its own file.

Mark each finding with the prefix `[migration]`.
