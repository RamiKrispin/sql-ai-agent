# 05 — Model Performance & Evaluation

> Goal: Show the workflow for choosing a model — define test cases, run them across providers/models, compare success rate vs. latency vs. cost — and look at pre-computed results from the repo.

## Overview — why eval matters

Context shapes the question. Guardrails shape the action. The third lever is
the model itself, and choosing one isn't obvious. The model card won't tell us
how a model handles `air_traffic`. Pricing tier won't tell us either. Brand
won't tell us at all.

Without an eval, model selection collapses to vibes. We pick the model whose
name is loudest this quarter, ship it, and find out in production whether it
can actually answer the questions our users ask. That's a bad place to learn.

An eval flips the order. We define what "working" means before we pick. Then
we let the numbers pick.

## The eval framework in this repo

The `sql_ai_agent.testing` package gives us four pieces:

- **`TestCase`** — one question plus a validator that knows what a correct
  answer looks like (row count, expected columns, expected value).
- **`TestRunner`** — wires a model into a real `SqlAgent`, runs every test
  case against it, and records success, latency, and the SQL it produced.
- **`get_test_cases()`** — returns the suite. Today: **20 test cases**, split
  **5 easy / 8 medium / 7 hard**, across 11 categories — basic, aggregation,
  filtering, comparison, ranking, time series, growth analysis, percentage,
  market share, complex filtering, and edge cases.
- **`get_test_summary()`** — the breakdown view we open at the top of the
  notebook to remember what's in the suite.

Each model under test gets the full **20 query-generation tests** plus
**5 debug-mechanism tests** — the latter feed an intentionally broken query
into the agent and check whether the debug agent can repair it. Twenty-five
runs per model.

## What we measure

Three top-line metrics carry the comparison:

- **Success rate** — percent of generation tests where the agent's SQL ran
  and returned the expected result on the first try.
- **Avg execution time** — wall-clock seconds per generation test. Almost
  entirely the LLM; the DB call is fast.
- **Fix rate** — percent of broken queries the debug agent successfully
  repaired within the retry budget. This is where the guardrails from
  Topic 04 meet the model.

Three numbers, three different questions. A model can be strong on one and
weak on another, and the eval is what surfaces it.

## Demo — walking through the pre-computed results

We won't re-run the matrix live. The most recent run is already saved under
`notebook/` with timestamp `20260503_150027`. We walk through it in the
notebook and the three HTML plots.

1. Open `notebook/03_model_eval.ipynb`. Run the **test summary** cell — 20
   tests, the difficulty split, the 11 categories. This is the suite every
   model is being graded against.
2. Skim the **`models_to_test`** cell. Eight models in the run: five from
   OpenAI (`gpt-5.5`, `gpt-5.5-pro`, `gpt-5.4-nano`, `gpt-5.4-mini`,
   `gpt-4.1`) and three local via Docker Model Runner
   (`ai/granite-4.0-h-micro`, `ai/llama3.2:latest`, `ai/gemma4:100k`).
3. Open the **comparison table** cell (`comparison_df`). The headline numbers
   from this run:

   | Model                   | Provider             | Success rate | Avg time (s) | Fix rate    |
   | ----------------------- | -------------------- | ------------ | ------------ | ----------- |
   | `gpt-5.4-mini`          | openai               | 90.00%       | 1.192        | 100%        |
   | `gpt-5.5`               | openai               | 90.00%       | 5.723        | 100%        |
   | `gpt-4.1`               | openai               | 80.00%       | 0.825        | 100%        |
   | `ai/granite-4.0-h-micro`| docker_model_runner  | 70.00%       | 2.828        | 80%         |
   | `ai/gemma4:100k`        | docker_model_runner  | 65.00%       | 1.956        | 100%        |
   | `gpt-5.4-nano`          | openai               | 50.00%       | 3.376        | 100%        |
   | `ai/llama3.2:latest`    | docker_model_runner  | 40.00%       | 1.577        | 80%         |
   | `gpt-5.5-pro`           | openai               | 0.00%        | 0.117        | (no run)    |

4. Open `notebook/success_rates_20260503_150027.html`. Bar chart of the
   success-rate column. The story to read off the chart: `gpt-5.4-mini` ties
   `gpt-5.5` at **90%** while running roughly **5x faster** (1.2s vs 5.7s).
   The cheaper model is the better product here.
5. Open `notebook/execution_times_20260503_150027.html`. The latency
   ranking. `gpt-4.1` is the fastest at 0.8s; `gpt-5.5` is the slowest at
   5.7s. Both clear 80% on accuracy. For an interactive UI the choice is
   obvious; for a nightly batch job it's less so.
6. Open `notebook/difficulty_heatmap_20260503_150027.html`. Success rate
   broken out by easy / medium / hard. A model that scores 100% on easy and
   30% on hard is not the same product as one that scores 70/70/70 — the
   heatmap is the only place that shows up.
7. Call out the `gpt-5.5-pro` row. Zero successes, 0.117s "average" time —
   the run was failing fast on a `404 not a chat model` config issue. The
   eval surfaced it. Branding and price tier hid it.

## What this means for shipping

Three rules for the next time we pick a model:

- **Define the tests first.** The test suite is the spec. Pick the model
  *after* it exists, not before.
- **Always include one cheap model and one local model in the comparison.**
  In this run, `gpt-5.4-mini` beat `gpt-5.5` on speed and tied on accuracy,
  and the local Docker models hit 65–70% — competitive with mid-tier hosted
  models, with the data never leaving the host. The default isn't always
  the right choice.
- **Re-run the eval whenever you change models or the prompt template.**
  Drift is real. A change to the system prompt can move the success rate
  several points in either direction; a model version bump can do the same.
  The eval is cheap to re-run; production regressions are not.

## Files in this topic

- `README.md` — this file.
- The walkthrough runs from `notebook/03_model_eval.ipynb` (already in the
  repo).
- The pre-computed results referenced above (already in the repo, do not
  regenerate during the workshop):
  - `notebook/test_summary_20260503_150027.csv`
  - `notebook/model_comparison_20260503_150027.csv`
  - `notebook/test_results_20260503_150027.csv`
  - `notebook/success_rates_20260503_150027.html`
  - `notebook/execution_times_20260503_150027.html`
  - `notebook/difficulty_heatmap_20260503_150027.html`
- The eval framework lives at `sql_ai_agent/testing/` —
  `framework.py` (the `TestRunner`), `test_cases.py` (the suite plus
  `get_test_cases` / `get_test_summary`), `debug_tester.py` (the
  fix-rate path).

## Recap & next

We've covered context, guardrails, and model selection — the three biggest
levers on a SQL AI agent's quality. Let's close with the practices that tie
them together.
