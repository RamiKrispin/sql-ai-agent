# 01 — What is a SQL AI Agent?

> Goal: Distinguish a SQL AI agent from a single LLM prompt; walk the seven-component pipeline (user question → prompt template → API handler → LLM API → parse the response → DB handler → send query to DB → return data); see it run live.

## Overview — prompt vs. agent

A single LLM call can write SQL. That's not the same as answering a data
question. The model returns text. It doesn't know our schema, it doesn't run
the query, and it doesn't hand back rows. If the SQL is broken, nothing tells
us. If the model invents a column, nothing catches it.

A **SQL AI agent** is the wrapper that closes those gaps. It composes a prompt
that includes the schema, calls the LLM, parses the response, runs the query
against the database, and returns data. One LLM call is one step inside that
loop — not the whole thing.

That's what we mean by "agent" in this workshop: an orchestrated pipeline
around the model, not a tool-using planner. We're going to keep the definition
narrow on purpose — Topic 02 is where production-grade pieces (validator,
fallback, memory, skills, logging) come in.

## The seven-component pipeline

The diagram in `assets/SQL AI Agent.drawio` lays out the whole flow. We walk
the seven components in order. Each one has a single responsibility.

1. **User question** — a natural-language request, e.g. `"How many passengers landed during 2024?"`. The pipeline starts here.
2. **Prompt template** — the structured text we send to the LLM, with placeholders for the table name, schema, and question. The simple version of this template lives in the demo notebook; the production version is `set_prompt_template()` in `sql_ai_agent/prompt_handler.py`.
3. **API handler** — the layer that takes the built prompt and calls the LLM API (model + provider + auth). In the demo this is a `ChatOpenAI` client pointed at Docker Model Runner.
4. **LLM API** — the model itself. The demo uses `gemma4:100k` running locally via Docker Model Runner (`http://model-runner.docker.internal/engines/v1`).
5. **Parse the response** — the model returns text; we need a clean SQL string. If the model wraps the SQL in a markdown fence, we strip it. The helpers `is_markdown_code_chunk` and `extract_code_from_markdown` in `sql_ai_agent/parse_query.py` do that job.
6. **DB handler** — the code path that connects to the database and runs the SQL. In this repo it's an Ibis connection plus `query_execute` and `get_tbl_attr` in `sql_ai_agent/db_handler.py`.
7. **Send query → return data** — the DB handler executes the SQL and returns a `DataFrame`. That's what the user gets back.

What we will *not* see in this topic: a SQL validator, a debug retry loop,
conversation memory, skill files, or logging. Those are the components that
turn this pipeline into something we'd put in front of a user. We'll add them
in Topic 02 onward.

## Demo walkthrough

Live demo: `notebook/02_simple_sql_ai_agent.ipynb`. We'll run it cell by cell.

The notebook is the seven-component pipeline at its smallest. Each cell maps
to one piece of the diagram:

| # | Cell does | Maps to component |
|---|---|---|
| 1 | Imports + adds project root to `sys.path` | — |
| 2 | Opens an Ibis connection to Postgres (`my_db`, table `air_traffic`) | DB handler (setup) |
| 3 | Defines `system_template` + `user_template`; builds a `ChatPromptTemplate` | Prompt template |
| 4 | Calls `get_tbl_attr(con, tbl_name)` to fetch the schema string | DB handler (introspection) |
| 5 | Configures `ChatOpenAI` with `base_url=http://model-runner.docker.internal/engines/v1`, `model="gemma4:100k"` | API handler + LLM API |
| 6 | Composes `chain = prompt_template \| llm` | Wires prompt template → API handler |
| 7 | Sets `question = "How many passengers landed during 2024?"` | User question |
| 8 | `chain.invoke({...})` returns the LLM output | LLM API call |
| 9 | `query = llm_output.content; print(query)` | Parse the response (here, no markdown to strip) |
| 10 | `con.sql(query).execute()` runs the SQL and returns a DataFrame | DB handler → return data |
| 11 | Wraps the whole flow as `basic_sql_agent(chain, question, tbl_name, schema, con)` | All seven components in one function |

The question we'll run live is the same one in the notebook:
`"How many passengers landed during 2024?"`. With the `air_traffic` table,
`gemma4:100k` returns a query of the shape
`SELECT SUM("Passenger Count") FROM "air_traffic" WHERE "Year" = 2024`,
and the DB returns a single number — the 2024 passenger total.

Two things to notice while it runs:

- **The schema is the agent's only knowledge of the table.** That string
  goes into the system prompt verbatim. If we don't pass it, the model has
  to guess column names — that's the failure mode we'll fix with context
  layers in Topic 03.
- **There's no safety net.** If the model invents a column, the DB raises an
  error and the cell fails. There's no validator and no retry. Topic 02
  introduces both.

## Files in this topic

- `README.md` — this file.
- The demo runs from `notebook/02_simple_sql_ai_agent.ipynb` (already in the repo; we don't duplicate it).
- The reference diagram is `assets/SQL AI Agent.drawio` (already in the repo).

## Recap & next

We've drawn the line between a single LLM call and a SQL AI agent: the agent
is the seven-component pipeline that gets us from a question to a row of
data. We watched the smallest version of it run end-to-end against
`air_traffic` with `gemma4:100k`.

Next, in Topic 02, we'll see what changes when we move this pipeline from a
notebook into production — what components show up, and why a "production"
agent looks different from this one.
