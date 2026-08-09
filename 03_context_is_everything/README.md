# 03 — Context is Everything

> Goal: Show why context is the single biggest lever on agent quality, and walk three context layers — schema + distinct values, domain skills, conversation memory — live in the Streamlit app.

## Overview

Topic 02 named the layers a production SQL AI agent needs. Now we open the
first of them — the context layer — because it's the one that moves the
quality needle the most.

Here's the claim, stated plainly: **the same model with better context beats
a bigger model with worse context.** Most agent failures we've debugged
weren't model failures. The model was fine. It was guessing column names,
inventing enum values, or losing track of what we asked two questions ago.
That's a context gap, not a reasoning gap.

We say "why before what" a lot in this workshop. The "why" of context is
that an LLM only knows what we put in the prompt. Schema, business rules,
prior turns of the conversation — none of it is implicit. If we want the
agent to behave like someone who knows our data, we have to *show* it the
data. That's all the context layer is.

## The three context layers

The repo wires three distinct layers of context into the prompt. Each one
fixes a different failure mode. The diagram in
`context_layers.drawio` shows all three feeding into the prompt template.

### 1. Schema + distinct values

**What it is.** The structural description of the table. Two pieces:

- The schema — column names and types — as a `CREATE TABLE` line. Always
  on. This is the baseline every prompt gets.
- The **distinct values** — sample categorical values for string columns.
  Opt-in. Tells the model that `"Activity Type Code"` holds
  `'Deplaned'`, `'Enplaned'`, `'Thru / Transit'` — and not `'arrival'`
  or `'departure'`, which is what an LLM will guess if we don't say.

**How it's wired.** `get_tbl_attr` in `sql_ai_agent/db_handler.py` pulls
the schema. `get_character_distinct_values` in the same file walks every
character column and runs `SELECT DISTINCT ... LIMIT max_values` (default
50). `format_distinct_values_for_prompt` in
`sql_ai_agent/prompt_handler.py` formats the result as bullet points.
`SqlAgent.ask_question(distinct_char_values=True)` appends the formatted
block to `additional_context` before the prompt is rendered. The
Streamlit app exposes this as the **"Include Distinct Character Values"**
checkbox in the sidebar.

**What the demo shows.** Toggle distinct values off, ask a question that
depends on enum values, and watch the agent guess wrong.

### 2. Skills (domain knowledge)

**What it is.** A markdown file under `skills/` that encodes the things
a human analyst would know but a generic LLM won't. For our running
example, `skills/sfo_air_traffic_context.md` (~250 lines) covers:

- A schema reference with what each column actually means
  (e.g., `Deplaned` = arrival, `Enplaned` = departure,
  `Thru / Transit` = connecting passengers).
- Critical best practices: exclude transit when counting "total
  passengers", use `Operating Airline` not `Published Airline` to avoid
  codeshare double-counting, quote columns with spaces.
- Common query patterns (top airlines, international vs domestic,
  low-fare carriers).
- Percentage and growth-rate rules — e.g., always divide by the prior
  period for year-over-year growth, guard against zero denominators.
- A pitfalls table with the things humans get wrong on this dataset.

**How it's wired.** `SkillManager.load_skill(...)` in
`sql_ai_agent/skill_manager.py` reads the markdown file. `SqlAgent.__init__`
tries three filename patterns when `skill=True` is passed:
`<tbl_name>`, `<tbl_name>_context`, `sfo_<tbl_name>_context`. For our
table `air_traffic`, the third pattern matches `sfo_air_traffic_context.md`.
The content is appended to `additional_context` inside `ask_question`.

**What the demo shows.** A domain-specific question — for example,
year-over-year passenger growth — produces a more correct query when the
skill is loaded (transit excluded, prior-period denominator, NULLIF guard)
than when it isn't.

### 3. Conversation memory

**What it is.** A buffer of prior user/assistant turns, so the agent can
resolve follow-up questions like *"what about 2023?"* against the
previous turn.

**How it's wired.** `SqlAgent` holds an `InMemoryChatMessageHistory` from
`langchain_core`. The prompt template includes a
`MessagesPlaceholder(variable_name="chat_history")` (see
`set_prompt_template` in `sql_ai_agent/prompt_handler.py`). When
`memory=True`, every Q&A pair is appended to the history; `_trim_memory`
caps the buffer at `memory_size` pairs (FIFO). The Streamlit app exposes
this as **"Enable Conversation Memory"** plus the **"Memory Size"**
slider.

**What the demo shows.** Ask a question, then ask a vague follow-up.
With memory on, the agent resolves the reference. With memory off, it
can't.

## Demo: turning context on and off in `app/agent_app.py`

Run the Streamlit app (`uv run streamlit run app/agent_app.py`). Defaults
in the sidebar: **Conversation Memory** ON, **Memory Size** 10,
**Include Distinct Character Values** ON. We'll toggle one knob at a time.

1. **Baseline.** With defaults, ask:
   *"What activity type codes are in the database?"*
   The distinct-values block is in the prompt, so the agent should
   answer with the three real values: `Deplaned`, `Enplaned`,
   `Thru / Transit`.

2. **Distinct values OFF.** Untick **"Include Distinct Character
   Values"**. Ask the same question. The schema still tells the model
   the column exists, but not what's in it — so the model is free to
   guess. Common failure modes here: hallucinated values like
   `'arrival'` / `'departure'`, or a query that returns `DISTINCT` from
   the table (which works, but only because the agent knew to fall
   back to introspection).

3. **A question that needs the skill.** Re-enable distinct values.
   Ask a domain-specific question, e.g.:
   *"What's the year-over-year passenger growth from 2023 to 2024?"*
   Without the skill, two failure modes are common: the agent counts
   transit passengers (inflating the total), or it picks the wrong
   denominator (dividing by 2024 instead of 2023). With the skill
   loaded, the rules in `sfo_air_traffic_context.md` push the model
   toward the right query: filter `Activity Type Code IN ('Deplaned',
   'Enplaned')`, divide by the prior period, guard with `NULLIF`.

   **Honest limitation:** the Streamlit app doesn't currently expose a
   skill toggle in the sidebar. The skill is loaded at agent init —
   `SqlAgent(..., skill=True)`. To demo skill on/off live, either flip
   `skill=True/False` in `init_agent` in `app/agent_app.py` and rerun,
   or describe the difference and show the file. We're calling this out
   on purpose: the deck and the app are honest about what's wired.

4. **Memory ON → follow-up.** Ask:
   *"Show me passengers in 2024."*
   Then, as a separate turn:
   *"What about 2023?"*
   With memory on, the second question resolves against the first —
   the agent generates the same query shape with `"Year" = 2023`.

5. **Memory OFF → same follow-up.** Untick **"Enable Conversation
   Memory"**, click **"Clear Conversation"**, and repeat the two-step
   exchange. The first answer is the same. The second question now
   reaches the LLM with no chat history — the agent has no idea what
   "what about" refers to and either asks for clarification or guesses
   wrong.

Each toggle isolates one of the three layers. That's the point: context
isn't one knob. It's three.

## Files in this topic

- `README.md` — this file.
- `context_layers.drawio` — diagram of the three context layers feeding
  the prompt template, which then flows to the LLM API.

## Recap & next

Context is the cheapest, biggest quality lever we have. Schema + distinct
values keep the agent honest about what's in the table. Skills teach it
the domain. Conversation memory keeps a multi-turn chat coherent. All
three live in `additional_context` and `chat_history` on the prompt
template — one place to look when an answer goes sideways.

Context tells the agent what it should do. Guardrails decide what it's
*allowed* to do. That's where we go next.
