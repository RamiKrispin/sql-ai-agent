# 02 — SQL AI Agent in Production

> Goal: Define what "in production" means for this kind of system, and name the components that show up once you move past a notebook.

## Overview

We've seen the seven-component pipeline run end-to-end. The notebook works.
That's not the same as production. "Production" here doesn't mean *more code*.
It means *more concerns*: correctness when the model returns broken SQL, safety
when it returns a destructive statement, observability when something goes
wrong overnight, cost when the picked model is over-spec, and evolvability
when next month we need to swap providers or add a domain.

The gap we're describing is the gap between `notebook/02_simple_sql_ai_agent.ipynb`
and `app/agent_app.py`. Same pipeline at the core. New layers around it.

## From notebook to production: what changes

The seven-component pipeline from Topic 01 is still here. We don't replace it.
We *wrap* it. The agent core (`sql_ai_agent/SqlAgent.py`) keeps the same
prompt → API → parse → DB shape, then adds: an application layer to take
input, a context layer to enrich the prompt, a safety layer to vet the output,
a reliability layer to retry and fall back, and an observability layer to
record what happened. Each new layer answers one of the production concerns
above.

## The components of a production SQL AI agent

We group the modules into six layers. Each layer is named here. The how-it-works
deep dive is reserved for Topics 03–05.

### Application layer

- `app/agent_app.py` — the Streamlit chatbot. Takes the user question, renders
  results, exposes settings (model, memory, read-only, enforce-limit, logging).

### Agent core

- `sql_ai_agent/SqlAgent.py` — the `SqlAgent` class that orchestrates the
  pipeline. Holds the prompt template, the primary chain, the validator, the
  DB connection, and the debug retry loop.
- `sql_ai_agent/parse_query.py` — strips markdown fences from the LLM output
  before the SQL reaches the DB.
- `sql_ai_agent/db_handler.py` — the Ibis connection, `get_tbl_attr`,
  `query_execute`, `get_character_distinct_values`.

### Context layer

- `sql_ai_agent/prompt_handler.py` — `set_prompt_template`,
  `format_distinct_values_for_prompt`, `debug_prompt_template`.
- `sql_ai_agent/skill_manager.py` — `SkillManager`. Loads markdown skill files
  from `skills/` and injects their content into the prompt.
- Conversation memory — `InMemoryChatMessageHistory` plus `_trim_memory` inside
  `SqlAgent`. (Topic 03 opens all three.)

### Safety layer

- `sql_ai_agent/sql_validator.py` — `SQLValidator`, `ValidationConfig`,
  `enforce_limit`. Read-only mode, multi-statement protection, LIMIT
  enforcement. (Topic 04 opens it.)

### Reliability layer

- The debug retry loop in `SqlAgent.ask_question` — re-prompts the LLM with the
  failed query and the error message, up to `trials` retries, using
  `prompt_handler.debug_prompt_template`.
- Fallback model — a second model the agent switches to if the primary chain
  keeps failing. Configured in `llm_config.yaml` (`fallback_model`,
  `enable_fallback`) and via `SqlAgent(fallback=True, fallback_model=...)`.
- Configuration — `llm_config.yaml` plus `sql_ai_agent/llm_config_loader.py`.
  Provider, model, temperature, fallback, and per-provider settings live here,
  not in code.

### Observability layer

- `sql_ai_agent/logger.py` — structured logging (human or JSON).
- `sql_ai_agent/callbacks.py` — LangChain callback that captures token counts
  and timing on every LLM call.
- `sql_ai_agent/log_database.py` — DB-backed log handler for persistent runs.
- `sql_ai_agent/testing/` — the eval framework (`TestRunner`, `TestCase`).
  Offline eval, not runtime. (Topic 05 opens it.)

## Files in this topic

- `README.md` — this file.
- `production_architecture.drawio` — the production-architecture diagram for
  this topic. Shows the seven-component core wrapped by the six layers above,
  with the database, configuration, and observability rails attached.

## Recap & next

We've named what production demands and where each piece lives in the repo.
Now that we know which components production demands, we'll spend the next
three sections on the three biggest ones — context, guardrails, and model
choice. Context is first.
