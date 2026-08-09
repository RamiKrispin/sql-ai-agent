# 04 — SQL AI Agent Guardrails

> Goal: Make safety concrete: admin control (read-only mode), SQL validation (sqlglot), and constraints (LIMIT enforcement). Demoed in the Streamlit app by attempting a destructive query.

## Overview — why guardrails exist

Context tells the agent what it should do. Guardrails decide what it's
*allowed* to do.

The LLM is generating SQL. That SQL runs against our database. If the model
returns `DROP TABLE air_traffic`, something on our side has to stop it before
it reaches the connection. That's the validator's job: it sits between the
LLM and the DB handler, and it's the only thing in the pipeline that knows
the difference between "answer the question" and "modify the table."

Even in a sandbox, we still want a `LIMIT`. A model that writes
`SELECT * FROM air_traffic` against a 50-million-row table will happily
return 50 million rows. That kills the workshop laptop and floods the
chat UI. The validator's `enforce_limit` step is a small constraint with a
big payoff.

Three guardrails ship with the agent. We'll walk each one, then break things
on purpose in the app.

## Three guardrail types

### 1. Admin control — read-only mode

In read-only mode, only `Select`, `With`, `Show`, and `Describe` are allowed.
Everything else — `INSERT`, `UPDATE`, `DELETE`, `DROP`, `ALTER`, `TRUNCATE`,
`CREATE` — is blocked at the validator before it ever reaches the database.

- **Defined in:** `ValidationConfig` in `sql_ai_agent/sql_validator.py`
  (`read_only=True`, `allowed_statements=["Select", "With", "Show", "Describe"]`).
- **Enforced by:** `SQLValidator.validate(query)` — parses the query with
  `sqlglot`, gets the statement class names, and rejects any statement type
  not in `allowed_statements`.
- **Sidebar control:** `app/agent_app.py` — the "Read-Only" checkbox under
  *SQL Safety & Validation* (default on).
- **Default:** on, both in `llm_config.yaml` (`agent.read_only: true`) and in
  `SqlAgent(read_only=True)`.

This is the admin control: a deployer turns it on for end-user-facing apps,
and turns it off only inside an internal admin tool with the right DB
permissions to back it up.

### 2. SQL validation — what `sqlglot` catches

The validator parses the query before anything else. That gives us two checks
for free:

- **Multi-statement protection.** `sqlglot.parse(query)` returns a list. If the
  list has more than one item, the validator rejects the query. That blocks
  the classic injection shape — `SELECT 1; DROP TABLE air_traffic` — at parse
  time, regardless of read-only mode.
- **Conservative parse failure.** If `sqlglot` can't parse the string at all,
  the validator returns `False` with `"Unable to parse query: ..."`. We don't
  pass un-parseable text to the database. The default is to block, not to
  guess.

Empty queries are also rejected (`"Empty query not allowed"`).

- **Defined in:** `SQLValidator.validate(query)` in `sql_ai_agent/sql_validator.py`.
- **Returns:** a tuple `(is_valid: bool, error_message: Optional[str])` —
  consumed by `query_processing` in `SqlAgent.py`.

### 3. Constraints — LIMIT enforcement

Even a perfectly valid `SELECT *` is dangerous on a large table. The
validator's `enforce_limit(query)` adds a `LIMIT` clause if the query doesn't
have one, and rewrites the limit down if the existing one is larger than
`max_limit`.

- **Defined in:** `SQLValidator.enforce_limit` in `sql_ai_agent/sql_validator.py`.
  Uses `sqlglot.parse_one(query)` and `parsed.limit(self.config.max_limit)`.
  Falls back to a string append if parse-rewrite fails.
- **Sidebar controls:** `app/agent_app.py` — the "Enforce Limit" checkbox
  and the "Limit Size" dropdown with options `[10, 100, 1000, 10000]`. The
  app defaults to **10** (smallest option) so demo questions return small
  result sets.
- **Defaults in config:** `llm_config.yaml` sets `max_result_limit: 10000`
  and `enforce_limit: true`.

The "Rows Count" metric shown in the same sidebar block (the table's total
row count) is the foil to this — it lets us show how much of the table the
LIMIT is hiding.

## Demo — trying to break the agent in `app/agent_app.py`

We open the Streamlit app with the default sidebar settings: read-only on,
enforce limit on, limit = 10. Six attempts, in order:

1. **Drop the table.** Ask: `Drop the air_traffic table.` The LLM
   generates `DROP TABLE air_traffic`. The validator rejects it with
   `Operation not allowed: Drop. Only SELECT queries permitted in read-only mode.`
   No SQL hits the DB.
2. **Delete rows.** Ask: `Delete all rows where Year is 1999.` The model
   produces a `DELETE` statement. Same outcome — blocked, read-only.
3. **Update rows.** Ask: `Update Operating Airline to 'X' for terminal 1.`
   Blocked at validation. Same path.
4. **`SELECT *` against the limit.** Ask: `Show all rows in the table.` The
   validator allows the `SELECT`, then `enforce_limit` rewrites it to add
   `LIMIT 10`. Only 10 rows come back, even though the "Total Rows" metric
   in the sidebar shows millions. Bump the limit to `100` in the dropdown
   and re-ask — now 100 rows come back.
5. **Multi-statement.** Ask: `Show me 2024 data; DROP TABLE air_traffic.` If
   the LLM emits both statements, `sqlglot.parse` returns a list of length
   two and the validator blocks with
   `Multiple SQL statements detected. Only single statements allowed.`
6. **Read-only off — and an honest caveat.** Toggle the "Read-Only"
   checkbox off in the sidebar. Re-ask the DROP. The validator will now let
   it through (read-only is the gate). What happens after that depends on
   the database connection's own permissions. The app's job ends at the
   validator; the DB's job is the second line of defense. Don't ship a
   customer-facing app with this off.

## Why blocked queries skip retry and fallback

The debug agent and the fallback model are correctness mechanisms — they
exist for queries that *fail*, not for queries that are *not allowed*.
`SqlAgent.ask_question` makes that distinction explicit: if validation
fails in read-only mode, it returns immediately. No retry. No fallback.

Safety beats correction. Don't give the agent a second chance to ask for
a destructive query.

## Files in this topic

- `README.md` — this file.
- `sample_destructive_queries.md` — the six demo prompts and their
  expected validator outcomes, ready to paste into the Streamlit app.

## Recap & next

We've made the three guardrails concrete: admin control (read-only),
validation (`sqlglot` parsing, multi-statement block, conservative
defaults), and constraints (`enforce_limit`). They're the layer between
the LLM's output and the database, and they refuse to negotiate.

Context shapes the question; guardrails shape the action. The third lever
is the model itself — and choosing one isn't obvious. That's Topic 05.
