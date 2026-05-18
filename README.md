# Steward Systems BCT LLM Agent Challenge

A Nigerian-contextualised behavioural intelligence agent for review simulation and personalised recommendation.

Built for **Team Steward Systems** in the **DSN x BCT LLM Agent Challenge / Data & AI Summit Hackathon 3.0**.

## Competition Tasks Covered

- **Task A: User Modelling / Review Simulation** - predicts a 1-5 star rating and generates a realistic review from user persona/history and item details.
- **Task B: Personalised Recommendation** - returns ranked recommendations from persona, context, candidate domain, and local sample items.

## Architecture Overview

The application is a local FastAPI service with deterministic agent logic. Phase 2 strengthens the original foundation with richer behavioural profiling, transparent scoring breakdowns, and a larger Nigerian-context sample dataset:

- `app/api/` contains thin FastAPI route handlers.
- `app/agents/` orchestrates Task A and Task B workflows.
- `app/services/` contains profile building, retrieval, rating prediction, review generation, ranking, and Nigerian context logic.
- `UserProfileBuilder` extracts average rating, rating strictness, category affinity, positive preference signals, complaint signals, tone markers, price sensitivity, delivery sensitivity, spice tolerance, and portion preference.
- `NigerianContextAdapter` scores affordability, value for money, pepper/spice fit, delivery delay, Lagos/context cues, group meals, and local food/drink matches.
- `RecommendationRankingService` exposes the hybrid score components for each recommendation.
- `data/sample/` contains small JSON data that runs out of the box.
- `evaluation/` contains metric scripts for both tasks.
- `frontend/streamlit_app.py` provides an optional local demo UI.

No Supabase, authentication, RBAC, payments, or production SaaS complexity is included.

## Setup

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
uvicorn app.main:app --reload
```

Visit:

- [http://localhost:8000](http://localhost:8000)
- [http://localhost:8000/docs](http://localhost:8000/docs)
- [http://localhost:8000/health](http://localhost:8000/health)

## Docker

```bash
docker build -t steward-bct-agent .
docker run -p 8000:8000 --env-file .env steward-bct-agent
```

## Docker Compose

```bash
docker compose up --build
```

## API Endpoints

### `GET /`

Returns project information and available endpoints.

### `GET /health`

Returns service health.

### `POST /api/task-a/simulate-review`

Example request:

```json
{
  "user_persona": {
    "user_id": "user_001",
    "description": "A Lagos-based university student who likes spicy food, affordable meals, and fast delivery.",
    "past_reviews": [
      {
        "item_name": "Jollof Rice and Chicken",
        "category": "Food",
        "rating": 4,
        "review": "The food was tasty and the portion was fair, but delivery took too long."
      }
    ]
  },
  "item": {
    "item_id": "item_001",
    "name": "Spicy Chicken Shawarma",
    "category": "Food",
    "price": 2500,
    "metadata": {
      "spicy": true,
      "delivery_time_minutes": 35,
      "portion_size": "medium",
      "location": "Lagos"
    }
  }
}
```

Example response fields:

```json
{
  "predicted_rating": 4.4,
  "generated_review": "The Spicy Chicken Shawarma was a solid option...",
  "behavioural_reasoning_summary": "Predicted 4.4/5...",
  "positive_signals": ["spice level matches the user's pepper preference"],
  "negative_signals": [],
  "confidence": 0.62,
  "user_profile_summary": "balanced reviewer with interest in Food..."
}
```

Curl example:

```bash
curl -X POST http://localhost:8000/api/task-a/simulate-review ^
  -H "Content-Type: application/json" ^
  -d "{\"user_persona\":{\"user_id\":\"demo\",\"description\":\"A Lagos student who likes affordable spicy food and quick delivery.\",\"past_reviews\":[]},\"item\":{\"item_id\":\"item_001\",\"name\":\"Spicy Chicken Shawarma\",\"category\":\"Food\",\"price\":2500,\"metadata\":{\"spice_level\":4,\"delivery_time_minutes\":35,\"portion_size\":\"medium\",\"location\":\"Lagos\",\"tags\":[\"shawarma\",\"spicy\",\"quick\"]}}}"
```

### `POST /api/task-b/recommend`

Example request:

```json
{
  "user_persona": {
    "user_id": "user_001",
    "description": "A Lagos-based university student who prefers affordable spicy meals and quick delivery.",
    "past_reviews": []
  },
  "current_context": "Needs dinner after lectures and wants something filling but not expensive.",
  "top_k": 5
}
```

Response includes ranked recommendations, score, reason, context fit explanation, cold-start note, and ranking formula.

Each recommendation includes:

- `rank`
- `item_id`
- `item_name`
- `category`
- `final_score`
- `score_breakdown`
- `reason`
- `context_fit`
- `cold_start_note` when no past reviews are supplied

Curl example:

```bash
curl -X POST http://localhost:8000/api/task-b/recommend ^
  -H "Content-Type: application/json" ^
  -d "{\"user_persona\":{\"user_id\":\"cold_start_demo\",\"description\":\"Cold-start Lagos visitor who wants affordable local food, not too much pepper, and quick delivery near Yaba.\",\"past_reviews\":[]},\"current_context\":\"Needs a light dinner after a long day.\",\"top_k\":5}"
```

The ranking formula is:

```text
final_score = 0.30 semantic_similarity
            + 0.25 preference_match
            + 0.20 context_match
            + 0.15 item_quality_or_popularity
            + 0.10 nigerian_context_match
```

If embeddings are not configured, the app uses deterministic TF-IDF-style lexical similarity.

## Evaluation

```bash
python evaluation/evaluate_task_a.py
python evaluation/evaluate_task_b.py
pytest
```

Task A reports number of examples, RMSE, MAE, predicted-vs-actual samples, and qualitative generated-review samples. Task B reports Hit Rate@5, Hit Rate@10, NDCG@5, NDCG@10, and an ablation comparison:

- popularity/content baseline
- hybrid ranking without Nigerian context
- hybrid ranking with Nigerian context

Result files are written to:

- `evaluation/results/task_a_results.json`
- `evaluation/results/task_b_results.json`
- `evaluation/results/ablation_summary.json`

## Optional Streamlit Demo

```bash
streamlit run frontend/streamlit_app.py
```

The demo has two tabs: **Simulate Review** and **Recommend Items**.

## Dataset Disclosure

The repository includes a lightweight synthetic sample dataset:

- 18 Nigerian-context user personas
- 60 items across food, drinks, products, books, and movies
- 160 sample reviews
- cold-start users with no review history
- metadata for price, `spice_level`, delivery time, portion size, location, tags, popularity score, and average rating

The data is intentionally small for reproducibility. `data/raw/` is reserved for future datasets and ignored by git.

## Model and Framework Disclosure

The system uses deterministic, explainable Python services rather than a required LLM call. It includes lexical TF-IDF-style similarity implemented locally, profile heuristics, metadata scoring, and Nigerian-context rules. LLM integration is environment-gated through `.env` and can be added later without breaking deterministic fallback mode.

Deterministic fallback mode means judges can run the full API, tests, and evaluation scripts without an API key, network model call, live database, or hidden service.

## Nigerian Contextualisation

The Nigerian context adapter interprets affordability, value for money, pepper/spice preference, portion size, delivery delay, Lagos traffic sensitivity, mainland/island cues, family/group meals, and light Nigerian English tone. It includes local examples such as jollof rice, suya, shawarma, amala, egusi, fried rice, pepper soup, asun, bole, zobo, Chapman, meat pie, puff-puff, grilled chicken, and small chops without turning the output into caricature.

The adapter is used in two places:

- Task A: adjusts rating prediction and review generation with local context signals.
- Task B: contributes the `nigerian_context_match` score and explanation text.

## Reproducibility Notes

- Runs locally from JSON files.
- Does not require a live database.
- Does not require API keys.
- Docker exposes FastAPI on port `8000`.
- `.env.example` contains only safe placeholders.
- Tests cover health, expanded sample data, Task A output shape, rating range, Task B output shape, cold-start recommendation, descending ranking scores, and evaluation script execution.
