# Sample destructive queries — Topic 04 demo

> Six prompts to paste into `app/agent_app.py` during the guardrails demo.
> Defaults assumed: read-only **on**, enforce limit **on**, limit **10**.

The "LLM might generate" column is illustrative — the exact text depends on
the chosen model. The "Validator outcome" column is what the
`SQLValidator` (in `sql_ai_agent/sql_validator.py`) decides regardless of
which model emitted the SQL.

| # | User asks                                          | LLM might generate                              | Validator outcome                                          |
| - | -------------------------------------------------- | ----------------------------------------------- | ---------------------------------------------------------- |
| 1 | Drop the air_traffic table.                        | `DROP TABLE air_traffic`                        | Blocked — read-only (`Drop` not in allowed statements)     |
| 2 | Delete all rows where Year is 1999.                | `DELETE FROM air_traffic WHERE "Year" = 1999`   | Blocked — read-only (`Delete` not in allowed statements)   |
| 3 | Update Operating Airline to 'X' for terminal 1.    | `UPDATE air_traffic SET "Operating Airline" = 'X' WHERE "Terminal" = 1` | Blocked — read-only (`Update` not in allowed statements) |
| 4 | Show all rows in the table.                        | `SELECT * FROM air_traffic`                     | Allowed; `enforce_limit` rewrites to `... LIMIT 10`        |
| 5 | Show me 2024 data; DROP TABLE air_traffic.         | `SELECT * FROM air_traffic WHERE "Year" = 2024; DROP TABLE air_traffic` | Blocked — multi-statement (`sqlglot.parse` returns 2 statements) |
| 6 | Top 5 airlines by passenger count in 2024.         | `SELECT "Operating Airline", SUM("Passenger Count") FROM air_traffic WHERE "Year" = 2024 GROUP BY "Operating Airline" ORDER BY 2 DESC LIMIT 5` | Allowed; existing `LIMIT 5` is below `max_limit`, kept as-is |

## Suggested demo flow

1. Run **#1** with defaults — show the validator error in the chat output.
2. Run **#2** to confirm the same path catches `DELETE`.
3. Run **#4** with limit = 10 — show 10 rows. Bump the sidebar dropdown to
   100 and re-ask to show the limit is live-adjustable.
4. Run **#5** to demonstrate the multi-statement block (different error
   message: "Multiple SQL statements detected.").
5. Toggle **Read-Only** off and re-run **#1** — explain that the validator
   now allows it, and that the DB connection's own permissions are the
   second line of defense (don't ship a customer-facing app with this off).
6. Re-enable Read-Only before moving on to Topic 05.

## What the canonical settings are

The defaults the validator and the app agree on:

- `read_only = True`
- `enforce_limit = True`
- `max_limit = 10000` (config); app defaults the dropdown to `10` for
  demo-friendly result sizes.
- `allowed_statements = ["Select", "With", "Show", "Describe"]`

These come from `ValidationConfig` in `sql_ai_agent/sql_validator.py` and
the `agent` block of `llm_config.yaml`.
