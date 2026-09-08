# 06 — Best Practices

> Goal: Distill the workshop into five take-home principles — context layer, skills, short/long-term memory, performance, model fallback. Recap-style; no new demos.

## Overview

This is the recap, not new material. We've defined the SQL AI agent and walked
the seven-component pipeline (Topic 01). We've named the components a
production-grade version needs (Topic 02). And we've spent the bulk of the
workshop on the three biggest levers: context (Topic 03), guardrails
(Topic 04), and model selection (Topic 05).

Five threads run through all of that. They're the practices to keep in mind
when you go build one of these. Each one points back to where it lives in the
repo — none of it is new.

## Five practices

**First: context is a data-engineering discipline.** Curating distinct values,
maintaining the skill file, and keeping schema docs current is engineering
work, not prompt-tweaking. Treat it like a pipeline you own. In this repo:
`prompt_handler.format_distinct_values_for_prompt`, the schema string from
`db_handler.get_tbl_attr`, and the skill file at
`skills/sfo_air_traffic_context.md`.

**Second: skills compound.** Write the domain knowledge down once, version
it, and let the agent (and humans) read the same file. Every new edge-case
rule you add benefits every future query the agent ever runs. The
`SkillManager` in `sql_ai_agent/skill_manager.py` is the load path; the file
is the asset.

**Third: short-term and long-term memory serve different jobs.** Short-term
memory is the in-process chat history that lets the agent answer follow-ups
in a session — that's `SqlAgent(memory=True, memory_size=N)`, demoed in
Topic 03. Long-term memory is a DB-backed log of past Q&A pairs the agent can
learn from across sessions; the repo has the logging side
(`sql_ai_agent/log_database.py`), and wiring it back into the prompt is a
worthwhile extension.

**Fourth: measure, don't guess.** Topic 05's eval is the answer to "which
model should we use?" Define the test cases, run them across providers, look
at success rate, fix rate, latency, and cost together. The cheapest model
that meets your success bar wins. Re-run the eval whenever you change the
prompt, the schema, the skill file, or the model. The framework is in
`sql_ai_agent/testing/`.

**Fifth: plan for the model to fail.** Hosted models rate-limit, time out,
and occasionally return un-parseable output. `SqlAgent(fallback=True,
fallback_model=...)` switches to a second model when the primary fails;
both are configured in `llm_config.yaml`. A locally-served model is a
strong fallback for hosted-model outages — it costs nothing and it's still
there when the network isn't.

## What's *not* in this workshop

We kept the scope narrow on purpose. Tool-using agents that go beyond SQL,
multi-agent orchestration, ReAct- and planner-style architectures, and
fine-tuning your own model are all out of scope today. They're the natural
next steps once the SQL agent is solid — and most of what we covered here
(context, guardrails, evaluation, fallback) carries over to those settings
unchanged.

## Closing

Five practices, one through-line: a SQL AI agent gets reliable when we treat
it as a system, not a prompt. Context is engineered, guardrails are enforced,
models are measured, and failure has a fallback. Thanks for following along.
