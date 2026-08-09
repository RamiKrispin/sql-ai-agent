# Open Items

> Blockers, deferrals, and follow-ups. Newest first. Check off when resolved
> and bump the date.

_Last updated: 2026-06-02_

- [ ] **User to review derived production-architecture diagram (Topic 02)** — Original reference image (`[Image #1]`) wasn't visible in the prompt. We derived the diagram from the repo modules under `sql_ai_agent/` plus the Streamlit app/UI layer. File: `02_sql_ai_agent_in_production/production_architecture.drawio`. If the original image differs, swap or edit.
- [ ] **User to review derived context-layers diagram (Topic 03)** — Same situation as above (`[Image #2]`). We derived the diagram from `prompt_handler.py`, `skill_manager.py`, and the memory pathway in `SqlAgent.py`. File: `03_context_is_everything/context_layers.drawio`. If the original image differs, swap or edit.
- [ ] **PDF reference deck** — `~/Downloads/SQL AI Agents.pdf` is in scope as a reference but cannot be rendered without poppler-utils installed locally. We relied on the repo + user outline as primary sources; if specific slides from the PDF need to be re-used, copy the relevant section into the spec or install poppler.
- [x] **Pre-computed eval artifacts to feature in Topic 05** — Defaulting to the most recent timestamped set (`*_20260503_150027`). 8 models, 195 test executions. Confirm or swap if a different run is preferred.
