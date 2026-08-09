# Continuity Ledger — SQL AI Agents in Production (workshop)

> **Read this before building any topic.** Append after each topic is approved.
> Keeps terminology and the running example consistent, and ensures each topic
> picks up where the previous one left off (the single deck flows as one story).

## Ledger — what each topic established

### 01 — What is a SQL AI Agent?  ·  status: complete
- **Introduced:** SQL AI agent (definition: pipeline, not single LLM call); the **seven-component pipeline** in order — user question → prompt template → API handler → LLM API → parse the response → DB handler → send query to DB → return data; prompt template (simple form, no `additional_context` / `chat_history`); API handler; DB handler (Ibis + `get_tbl_attr` + `query_execute`); parse-the-response step (`is_markdown_code_chunk`, `extract_code_from_markdown` from `sql_ai_agent/parse_query.py`); the running example (`air_traffic` table on Postgres, model `gemma4:100k` served via Docker Model Runner). Explicitly **not** introduced yet: validator, fallback model, conversation memory, skill / skill file, debug agent, distinct values, read-only mode.
- **State after this topic:** Working "simple" agent demoed end-to-end via `notebook/02_simple_sql_ai_agent.ipynb`. The example question — `"How many passengers landed during 2024?"` — produces `SELECT SUM("Passenger Count") FROM "air_traffic" WHERE "Year" = 2024` and returns the 2024 passenger total (52,210,939 rows in the demo run). The pipeline is wrapped as `basic_sql_agent(chain, question, tbl_name, schema, con)` in the notebook's last cell. No safety net (no validator, no retry).

### 02 — SQL AI Agent in Production  ·  status: complete
- **Introduced:** Production architecture grouped into six layers (Application · Agent core · Context · Safety · Reliability · Observability); module names mapped per layer (`app/agent_app.py`; `SqlAgent.py` / `parse_query.py` / `db_handler.py`; `prompt_handler.py` / `skill_manager.py` / `InMemoryChatMessageHistory`; `sql_validator.py`; debug retry loop / fallback model / `llm_config.yaml`; `logger.py` / `callbacks.py` / `log_database.py` / `testing/`); the new diagram file `02_sql_ai_agent_in_production/production_architecture.drawio`; the five production concerns (correctness · safety · observability · cost · evolvability).
- **State after this topic:** Attendees can see the full production picture as a diagram; they know which layer each module belongs to; they're set up for the deep-dives in Topics 03 (context), 04 (guardrails), and 05 (model selection). No demo run; concept-only topic.

### 03 — Context is Everything  ·  status: complete
- **Introduced:** Three context layers — Schema + distinct values; Skills (domain knowledge); Conversation memory. New canonical references: `get_character_distinct_values` in `db_handler.py`; `format_distinct_values_for_prompt` in `prompt_handler.py`; `SkillManager.load_skill(...)` (skill filename patterns: `<tbl>`, `<tbl>_context`, `sfo_<tbl>_context`); `InMemoryChatMessageHistory` + `_trim_memory`. The skill file contents (`skills/sfo_air_traffic_context.md`) — schema cheat sheet, business rules (exclude transit, codeshare double-counting, percentage/growth math), pitfalls. The new diagram file `03_context_is_everything/context_layers.drawio`.
- **State after this topic:** Attendees have seen the Streamlit demo with memory + distinct values toggles flipped on/off; they know the skill toggle is code-only today (honest limitation logged); they understand "context is the single biggest lever on agent quality" as the topic's claim. The running example expands: same `air_traffic` table, but now demoed via `app/agent_app.py` rather than the notebook.

### 04 — SQL AI Agent Guardrails  ·  status: complete
- **Introduced:** Three guardrail types — Admin control (read-only) · SQL validation (sqlglot-based parse, multi-statement protection, conservative parse-failure handling) · Constraints (LIMIT enforcement). Canonical config defaults: `read_only=True`, `max_limit=10000`, `enforce_limit=True`, `allowed_statements=["Select", "With", "Show", "Describe"]`. The design choice that **validation failure in read-only mode bypasses retry and fallback** ("safety beats correction"). The sample-queries file `04_guardrails/sample_destructive_queries.md` with six paste-ready demo prompts.
- **State after this topic:** Attendees have watched the validator block `DROP`, `DELETE`, `UPDATE`, and a multi-statement injection in the Streamlit app, and seen `enforce_limit` rewrite `SELECT *` to `... LIMIT 10`. They know the validator is the only thing that knows the difference between "answer" and "modify" — and that flipping read-only off opens the gate but the DB connection's permissions are the second line of defense.

### 05 — Model Performance & Evaluation  ·  status: complete
- **Introduced:** The eval framework — `TestCase`, `TestRunner`, `get_test_cases`, `get_test_summary` in `sql_ai_agent/testing/`. The 20-test suite (5 easy / 8 medium / 7 hard, 11 categories). Per-model run: 20 generation tests + 5 debug-mechanism tests. Three top-line metrics: success rate · avg execution time · fix rate. Eight models compared (5 OpenAI + 3 Docker Model Runner) in run `20260503_150027`. The pre-computed artifacts (`test_summary_*.csv`, `model_comparison_*.csv`, `test_results_*.csv`, `success_rates_*.html`, `execution_times_*.html`, `difficulty_heatmap_*.html`) all live under `notebook/`. Three rules for shipping: define tests first; include cheap + local models; re-run on every change.
- **State after this topic:** Attendees have seen the comparison table and three plots, with the headline finding (`gpt-5.4-mini` ties `gpt-5.5` at 90% / ~5× lower latency; `gpt-5.5-pro` 0% surfaced a config bug). They know how to run the framework themselves (`notebook/03_model_eval.ipynb`).

### 06 — Best Practices  ·  status: complete
- **Introduced:** Five take-home practices (recap-style, not new content) — Context as data engineering · Skills compound · Short/long-term memory serve different jobs · Measure don't guess · Plan for the model to fail. Out-of-scope acknowledgement (tool-using agents, multi-agent orchestration, ReAct/planner-style, fine-tuning) for honest framing. The closing line "Thanks for following along."
- **State after this topic:** Workshop closed. Attendees have a recap, an honest scope statement, and a closing note. Q&A follows (10 min).

## Promise tracker

> Each row is the forward bridge a topic owes to the next. The "Fulfilled by"
> column flips to ✅ once the next topic visibly delivers on the promise.

| From topic | Forward promise                                                                                                                            | Fulfilled by | Status |
| ---------- | ------------------------------------------------------------------------------------------------------------------------------------------ | ------------ | ------ |
| 01         | "We've seen the seven-component pipeline run end-to-end. Next, we'll see what changes when we move it from a notebook into production."     | 02           | ✅      |
| 02         | "Now that we know which components production demands, we'll spend the next three sections on the three biggest ones — context, guardrails, and model choice. Context is first." | 03           | ✅      |
| 03         | "Context tells the agent what it should do. Guardrails decide what it's *allowed* to do. That's where we go next."                          | 04           | ✅      |
| 04         | "Context shapes the question; guardrails shape the action. The third lever is the model itself — and choosing one isn't obvious."           | 05           | ✅      |
| 05         | "We've covered context, guardrails, and model selection. Let's close with the practices that tie them together."                            | 06           | ✅      |
| 06         | (closing) "These are the threads to pull on when you ship one of these. Thanks for following along."                                        | —            | n/a    |

## Canonical terminology

> Use these exact terms across all topics. Update the ledger when a new term
> is introduced.

- **SQL AI agent** — a system that turns a natural-language question into a SQL query, runs it, and returns data. More than a single LLM call; has a pipeline of components.
- **Prompt template** — the structured text we send to the LLM, with placeholders for the question, table, schema, and additional context. Lives in `sql_ai_agent/prompt_handler.py`.
- **API handler** — the layer that takes a built prompt and calls the LLM API (model + provider + auth).
- **DB handler** — the code path that connects to the database, runs a SQL string, and returns rows. In this repo it's the Ibis connection plus helpers in `sql_ai_agent/db_handler.py`.
- **Validator** — `SQLValidator` in `sql_ai_agent/sql_validator.py`. Parses the LLM's SQL with `sqlglot`, blocks non-SELECT statements in read-only mode, blocks multi-statement input, and (optionally) enforces a `LIMIT`.
- **Fallback model** — a second model the agent falls back to if the primary model fails. Configured in `llm_config.yaml` and in `SqlAgent(fallback=True, fallback_model=...)`.
- **Skill / skill file** — a markdown file under `skills/` that injects domain knowledge into the prompt. Loaded by `SkillManager` in `sql_ai_agent/skill_manager.py`. Example: `skills/sfo_air_traffic_context.md`.
- **Distinct values** — known categorical values for string columns, fetched once and injected into the prompt to reduce hallucination on enum-like columns. Built by `prompt_handler.format_distinct_values_for_prompt`.
- **Conversation memory** — a chat-history buffer that lets the agent answer follow-up questions. Configured by `SqlAgent(memory=True, memory_size=N)`; trimmed with `_trim_memory`.
- **Debug / debug agent** — the retry path that re-prompts the LLM with the failed query + error message. Up to `trials` retries; uses `prompt_handler.debug_prompt_template`.
- **Read-only mode** — a validator setting that allows only `Select`, `With`, `Show`, `Describe` statements (default `True`).
- **Test runner / test case** — `TestRunner` and `TestCase` in `sql_ai_agent/testing/`. The Topic 05 evaluation framework: 20 query-generation tests + 5 debug-mechanism tests per model.
- **Success rate / fix rate** — the two top-line metrics in the eval. Success rate = % of test queries that returned the expected result on the first try. Fix rate = % of broken queries the debug agent successfully repaired.
- **Application layer** — the user-facing surface (Streamlit at `app/agent_app.py` here).
- **Agent core** — the `SqlAgent` orchestrator + parsing + DB handler.
- **Context layer** — the bundle of schema, distinct values, skills, and conversation memory injected into the prompt.
- **Safety layer** — the validator and its config (read-only, multi-statement protection, LIMIT enforcement).
- **Reliability layer** — debug retry loop + fallback model.
- **Observability layer** — structured logging, LangChain callbacks, DB-backed log handler, plus the offline eval framework.

## Slide-deck running state

> The single workshop deck at `slides/workshop_slides.html` was rebuilt as a unified deck (~41 slides) covering all 6 topics with bumped typography (h1 108px, h2 72px, lead 36px, sub 34px) and a wider content max-width (1640px). The deck is one HTML file with the cross-fade transition + slim progress bar from `course-slide-deck/templates/base-deck.html` preserved.

- **Sections present:**
  - **A. Opening (3 slides):** Title · About this workshop · Agenda.
  - **B. Topic 01 (6 slides):** Section divider · Prompt vs. agent · Seven-component pipeline · Components→repo files · Demo cue · Topic takeaway.
  - **C. Topic 02 (5 slides):** Section divider · Five production concerns · Production architecture diagram · Six layers grid · Topic takeaway.
  - **D. Topic 03 (8 slides):** Section divider · Big-quote claim · Three-layer diagram · Layer 1 (schema + distinct values) · Layer 2 (skills) · Layer 3 (memory) · Demo cue · Topic takeaway.
  - **E. Topic 04 (6 slides):** Section divider · Three guardrails grid · ValidationConfig code · Sample destructive queries table · Safety-beats-correction quote · Topic takeaway.
  - **F. Topic 05 (9 slides):** Section divider · Why eval matters · Eval framework · Models tested · Headline results table · Charts reference · Headline finding · Three rules for shipping · Topic takeaway.
  - **G. Topic 06 (4 slides):** Section divider · Five practices · What's not in this workshop · Closing card with "Thanks for following along."
- **Total slide count:** 41.
- **Last topic to write the deck:** 06 (full rebuild).
