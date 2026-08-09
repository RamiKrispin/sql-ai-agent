# SQL AI Agents in Production — Workshop Spec

> The single source of truth for this workshop. Keep it current; every build step
> reads it first.

## Overview

- **Title:** SQL AI Agents in Production
- **Audience:** Data and ML engineers who are comfortable with Python and SQL and have called an LLM API at least once. No prior experience with agents required.
- **Prerequisites:** Working knowledge of Python, SQL, and the basic shape of an LLM chat API. Conceptual familiarity with LangChain helps but isn't required.
- **Goal:** Attendees leave able to (a) explain what separates a SQL AI agent from a single LLM call, (b) name the components a production-grade SQL agent needs, (c) reason about context, guardrails, and model selection as first-class design choices, and (d) recognize the trade-offs that show up when shipping one of these systems.
- **Duration / format:** 90 minutes total — ~80 min content + ~10 min Q&A. Live (in-person or virtual).
- **Profile:** `design-principles`
- **Build mode:** all-at-once

## Requirements

**Use / include**
- The existing repo at `/Users/ramikrispin/Personal/tutorials/sql-ai-agent/` as the source of every code reference, demo, and diagram.
- The simple-agent walkthrough in `notebook/02_simple_sql_ai_agent.ipynb` (Topic 01 demo).
- The Streamlit app `app/agent_app.py` for the context and guardrails demos (Topics 03 and 04).
- The model-evaluation walkthrough in `notebook/03_model_eval.ipynb` plus its pre-computed artifacts (`notebook/test_summary_*.csv`, `notebook/model_comparison_*.csv`, `notebook/success_rates_*.html`, `notebook/execution_times_*.html`, `notebook/difficulty_heatmap_*.html`) for Topic 05 (no live test run during the workshop).
- The existing component diagram at `assets/SQL AI Agent.drawio` for Topic 01.
- The supporting modules under `sql_ai_agent/` — `SqlAgent.py`, `prompt_handler.py`, `sql_validator.py`, `db_handler.py`, `parse_query.py`, `skill_manager.py`, `llm_config_loader.py`, `logger.py`, `callbacks.py`, `log_database.py`, `data.py`, `token_utils.py`, and `testing/` — as the grounding for everything we say about the architecture.
- The domain-knowledge skill file at `skills/sfo_air_traffic_context.md`.
- The previous workshop deck at `/Users/ramikrispin/Downloads/SQL AI Agents.pdf` as a reference, not a source. Re-derive content from the repo; cite the deck only when the repo is silent.

**Avoid / out of scope**
- Building agents that go beyond SQL (tool-using agents, ReAct-style planners, multi-agent systems).
- Vendor-specific deep dives (e.g., LangGraph internals, OpenAI function calling specifics).
- Live re-running of the full 195-test eval matrix during the workshop.
- Anything not visible in the referenced repo or notebooks. If a claim can't be traced to the repo, it must be flagged in `open-items.md` rather than fabricated.

## Materials & assets

- **Source repo:** `/Users/ramikrispin/Personal/tutorials/sql-ai-agent/`
- **Existing code / demos:**
  - `notebook/02_simple_sql_ai_agent.ipynb` — Topic 01 demo (a four-step prompt → LLM → parse → execute pipeline using `gemma4:100k` via Docker Model Runner).
  - `notebook/03_model_eval.ipynb` — Topic 05 demo, paired with the pre-computed CSV/HTML artifacts in `notebook/`.
  - `app/agent_app.py` — Streamlit chatbot used in Topics 03 and 04 (toggles for memory, distinct values, read-only, enforce-limit, limit size; logging; LLM provider/model picker).
  - `sql_ai_agent/` package — full agent source (Topics 02, 03, 04 reference these modules directly).
  - `skills/sfo_air_traffic_context.md` — the domain-knowledge skill loaded by `SkillManager`.
- **Templates / style:** profile `design-principles` (override in `spec/style/` if present).
- **Diagrams:**
  - Topic 01 reuses `assets/SQL AI Agent.drawio`.
  - Topic 02 needs a new `02_sql_ai_agent_in_production/production_architecture.drawio` (matched to the user's reference image).
  - Topic 03 needs a new `03_context_is_everything/context_layers.drawio` (matched to the user's reference image).
  - Both diagrams are blocked on the user re-pasting the reference images — see `open-items.md`.

## Agenda

Ordered topics (full detail in `agenda.md`):

| #  | Topic                            | Folder                                | Time   |
| -- | -------------------------------- | ------------------------------------- | ------ |
| 01 | What is a SQL AI Agent?          | `01_what_is_a_sql_ai_agent`           | 15 min |
| 02 | SQL AI Agent in Production       | `02_sql_ai_agent_in_production`       | 10 min |
| 03 | Context is Everything            | `03_context_is_everything`            | 12 min |
| 04 | SQL AI Agent Guardrails          | `04_guardrails`                       | 10 min |
| 05 | Model Performance & Evaluation   | `05_model_eval`                       | 15 min |
| 06 | Best Practices                   | `06_best_practices`                   |  8 min |
| —  | Q&A                              | —                                     | 10 min |

The deck opens with a short framing block (title + 1–2 "who/what/why" slides) before Topic 01's section divider. There is no separate folder for the framing block.

## Implementation plan & status

Build **all topics in sequence (all-at-once mode)**. Each topic still gets an independent content pass and QA pass; continuity is appended after each. One final review at the end.

| Topic | Folder                                | Status  |
| ----- | ------------------------------------- | ------- |
| 01    | `01_what_is_a_sql_ai_agent`           | complete |
| 02    | `02_sql_ai_agent_in_production`       | complete |
| 03    | `03_context_is_everything`            | complete |
| 04    | `04_guardrails`                       | complete |
| 05    | `05_model_eval`                       | complete |
| 06    | `06_best_practices`                   | complete |

- **Current target:** all topics complete; deck rebuilt as unified deck (41 slides) on 2026-06-03.

## Slides

A **single** deck for the whole workshop at `slides/workshop_slides.html`, with one section per topic. The opening framing slides + each topic's section share the same deck. Branding line: `SQL AI Agents in Production · Workshop`.

## Conventions

Topic folders `NN_topic_name`; supporting code/docs inside each topic folder. **No scripts** in workshop mode. Continuity: `spec/continuity.md`. Open items: `spec/open-items.md`.
