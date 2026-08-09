# Workshop Agenda — SQL AI Agents in Production

> Ordered list of topics. Folder names follow `NN_topic_name`. If we reorder, we
> renumber with no gaps. The workshop is 90 minutes total: ~80 minutes of
> content + ~10 minutes Q&A.

| #  | Topic                          | Folder                            | Goal                                                                                                                                                                                  | Time   | Depends on |
| -- | ------------------------------ | --------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------ | ---------- |
| 01 | What is a SQL AI Agent?        | `01_what_is_a_sql_ai_agent`       | Distinguish a SQL AI agent from a single LLM prompt; walk the seven-component pipeline (user → prompt template → API handler → LLM → parse → DB handler → query → data); see it run live. | 15 min | —          |
| 02 | SQL AI Agent in Production     | `02_sql_ai_agent_in_production`   | Define what "in production" means for this kind of system, and name the components that show up once you move past a notebook (validator, fallback, logger, skill manager, app/UI layer, observability). | 10 min | 01         |
| 03 | Context is Everything          | `03_context_is_everything`        | Show why context is the single biggest lever on agent quality, and walk three context layers — schema + distinct values, domain skills, conversation memory — live in the Streamlit app.  | 12 min | 01, 02     |
| 04 | SQL AI Agent Guardrails        | `04_guardrails`                   | Make safety concrete: admin control (read-only mode), SQL validation (sqlglot), and constraints (LIMIT enforcement). Demoed in the Streamlit app by attempting a destructive query.        | 10 min | 02         |
| 05 | Model Performance & Evaluation | `05_model_eval`                   | Show the workflow for choosing a model — define test cases, run them across providers/models, compare success rate vs. latency vs. cost — and look at pre-computed results from the repo. | 15 min | 02         |
| 06 | Best Practices                 | `06_best_practices`               | Distill the workshop into five take-home principles: context layer · skills · short/long-term memory · performance · model fallback. Recap-style; no new demos.                       |  8 min | all        |

## Notes

- Each topic gets a `NN_topic_name/` folder with a `README.md` and its supporting code/docs (diagrams, walkthroughs, demo scripts).
- The whole workshop shares one slide deck (`slides/workshop_slides.html`); each topic is a section in that deck, preceded by a section-divider slide.
- An optional opening framing block (title + 1–2 slides) lives at the start of the same deck, with no separate folder.
- The deck is **not** built topic-by-topic in isolation — each topic adds its section to the existing deck file. The QA pass after each topic verifies the deck still loads, the previous topic's section is intact, and the new section follows the slide patterns from `course-slide-deck`.
- **Demo timing:** Topic 01 runs the simple-agent notebook live (one cell at a time, ~3 min of demo). Topic 03 and Topic 04 use the Streamlit app at `app/agent_app.py` (toggle settings between questions). Topic 05 walks through pre-computed CSV/HTML artifacts under `notebook/`; we do **not** re-run the full eval matrix during the workshop.
- **Memory** is introduced as a context layer in Topic 03 (third layer, demoed via the app's "Memory Settings" sidebar). Topic 06 references it as a recap, not a new concept.
