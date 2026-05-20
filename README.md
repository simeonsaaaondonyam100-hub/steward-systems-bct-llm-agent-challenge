# Steward Systems Behavioural Intelligence Agent

**Nigerian-contextualised LLM agent for review simulation and personalised recommendation.**

Built by **Team Steward Systems** for the **DSN x BCT LLM Agent Challenge / Data & AI Summit Hackathon 3.0**.

## What This Project Does

This repository contains a clean, local, container-ready AI agent application for both competition tasks:

- **Task A - User Modelling / Review Simulation:** predicts a 1-5 rating and generates a realistic written review from a user persona/history and item details.
- **Task B - Personalised Recommendation:** returns ranked recommendations with score breakdowns, context fit, cold-start handling, and Nigerian-context explanations.

The system is deterministic by default. It does not require Supabase, authentication, a database, billing, or a paid API key.

## Quick Start

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
uvicorn app.main:app --reload
```

Open:

- `http://localhost:8000`
- `http://localhost:8000/health`
- `http://localhost:8000/docs`

## Docker

```bash
docker build -t steward-bct-agent .
docker run -p 8000:8000 --env-file .env steward-bct-agent
```

Or:

```bash
docker compose up --build
```

Docker build could not be verified in the current shell because Docker is not installed there, but the Dockerfile and Compose config are included.

## Live Deployment Notes

The app is Docker-ready for platforms such as Render or Railway. The container starts FastAPI with `uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}`, so it binds to `0.0.0.0` and uses the platform-provided `PORT` when available while defaulting to `8000` locally.

For Render/Railway, create a service from the GitHub repository and select the included Dockerfile. No required secrets are needed for the default deterministic demo. Optional LLM settings and optional Yelp Open Dataset ingestion are available for experimentation, but they are not required for the default judge-facing deployment.

## Endpoints

| Method | Path | Purpose |
|---|---|---|
| `GET` | `/` | Project info and endpoint list |
| `GET` | `/health` | Health check |
| `POST` | `/api/task-a/simulate-review` | Rating prediction and review generation |
| `POST` | `/api/task-b/recommend` | Personalised ranked recommendations |
| `GET` | `/docs` | Swagger/OpenAPI docs |

## Testing the API in Swagger Docs

After starting the server, open:

```text
http://localhost:8000/docs
```

Swagger/OpenAPI automatically displays schema placeholders such as `"string"`, `0`, and `{}`. These placeholders show the request shape only; they are not meaningful user inputs and should not be used as real test cases.

For proper testing, open [docs/sample_payloads.md](docs/sample_payloads.md). Copy one of the realistic Task A or Task B payloads, paste it into the Swagger request body, and click **Execute**.

- Task A endpoint: `POST /api/task-a/simulate-review`
- Task B endpoint: `POST /api/task-b/recommend`

The API includes guardrails for placeholder inputs. Task A rejects placeholder-only item names/categories with validation errors, while Task B treats insufficient or placeholder-only profile evidence as cold-start input.

The default judging path uses the bundled `data/sample/` files. Optional Yelp Open Dataset ingestion is available for real-dataset experimentation, but it is not required to run or evaluate the default containerised demo.

## Task A Example

Request:

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
      "spice_level": 4,
      "spicy": true,
      "delivery_time_minutes": 35,
      "portion_size": "medium",
      "location": "Lagos"
    }
  }
}
```

Expected response shape:

```json
{
  "predicted_rating": 5.0,
  "generated_review": "Human-style review text...",
  "behavioural_reasoning_summary": "Why the agent predicted this rating.",
  "positive_signals": ["price looks reasonable for a budget-conscious Nigerian user"],
  "negative_signals": [],
  "confidence": 0.68,
  "user_profile_summary": "generous reviewer with interest in Food..."
}
```

## Task B Example

Request:

```json
{
  "user_persona": {
    "user_id": "cold_start_demo",
    "description": "Cold-start Lagos visitor who wants affordable local food, not too much pepper, and quick delivery near Yaba.",
    "past_reviews": []
  },
  "current_context": "Needs a light dinner after a long day.",
  "top_k": 5
}
```

Expected response shape:

```json
{
  "recommendations": [
    {
      "rank": 1,
      "item_id": "item_014",
      "item_name": "Akara and Custard Combo",
      "category": "Food",
      "final_score": 0.52,
      "score_breakdown": {
        "semantic_similarity": 0.12,
        "preference_match": 0.85,
        "context_match": 0.34,
        "item_quality_or_popularity": 0.71,
        "nigerian_context_match": 0.88,
        "penalty": 0.0
      },
      "reason": "Recommended because ...",
      "context_fit": "price fits the current budget context",
      "preference_match_explanation": "mild spice fits user tolerance; price fits a value-conscious profile",
      "penalty_explanation": null,
      "cold_start_note": "Cold-start mode used..."
    }
  ],
  "profile_summary": "balanced reviewer...",
  "cold_start_note": "Cold-start mode used...",
  "ranking_formula": "final_score = ...",
  "semantic_mode": "tfidf_fallback"
}
```

More examples are in [docs/sample_payloads.md](docs/sample_payloads.md).

## Architecture

| Component | File(s) | Role |
|---|---|---|
| FastAPI app | `app/main.py`, `app/api/` | Stable HTTP API |
| Review simulation agent | `app/agents/review_simulation_agent.py` | Orchestrates Task A |
| Recommendation agent | `app/agents/recommendation_agent.py` | Orchestrates Task B |
| Profile builder | `app/services/user_profile_builder.py` | Rating strictness, preferences, complaints, tone, price/spice/portion signals |
| Nigerian context adapter | `app/services/nigerian_context_adapter.py` | Affordability, delivery, pepper, portion, Lagos/local cues |
| Semantic similarity | `app/services/semantic_similarity_service.py` | Optional sentence-transformer mode with TF-IDF fallback |
| Ranking service | `app/services/recommendation_ranking_service.py` | Hybrid scoring, penalties, explanations |
| Evaluation | `evaluation/` | Metrics, ablation, human rubric |

## Recommendation Formula

Selected by `scripts/tune_recommendation_weights.py` using a small explainable grid:

```text
final_score =
  0.18 * semantic_similarity
+ 0.38 * preference_match
+ 0.20 * context_match
+ 0.10 * item_quality_or_popularity
+ 0.10 * nigerian_context_match
- 0.04 * penalty
```

The default semantic mode is `tfidf_fallback`. Optional sentence-transformer mode can be enabled only when installed and explicitly configured:

```bash
set STEWARD_ENABLE_SENTENCE_TRANSFORMERS=true
set STEWARD_SENTENCE_TRANSFORMER_MODEL=sentence-transformers/all-MiniLM-L6-v2
```

The default Docker build does not download model weights.

## Evaluation

Run:

```bash
python evaluation/evaluate_task_a.py
python evaluation/evaluate_task_b.py
python scripts/tune_recommendation_weights.py
pytest
```

Current bundled-data metrics:

| Task | Metric | Value |
|---|---:|---:|
| Task A | RMSE | 0.703 |
| Task A | MAE | 0.546 |
| Task A | Avg generated review length | 70.9 words |
| Task B | Hit Rate@5 | 0.429 |
| Task B | Hit Rate@10 | 0.571 |
| Task B | NDCG@5 | 0.155 |
| Task B | NDCG@10 | 0.207 |

Task B uses a deterministic held-out split: early reviews form profile history, later reviews form test relevance labels, and known training items are removed from candidate pools.

## Ablation Summary

| Variant | HR@5 | HR@10 | NDCG@5 | NDCG@10 |
|---|---:|---:|---:|---:|
| Popularity baseline | 0.286 | 0.429 | 0.143 | 0.169 |
| Content-only baseline | 0.000 | 0.286 | 0.000 | 0.048 |
| Hybrid without Nigerian context | 0.286 | 0.571 | 0.121 | 0.194 |
| Hybrid with Nigerian context | 0.429 | 0.571 | 0.155 | 0.207 |

Full outputs:

- `evaluation/results/task_a_results.json`
- `evaluation/results/task_b_results.json`
- `evaluation/results/ablation_summary.json`
- `evaluation/results/ablation_summary.md`
- `evaluation/results/recommendation_weight_tuning.json`

Human evaluation support:

- `evaluation/human_eval_rubric.md`
- `evaluation/human_eval_examples.json`

## Dataset Disclosure

The included dataset is lightweight synthetic/demo data designed for reproducibility:

- 18 Nigerian-context user personas
- 60 items across food, drinks, books, movies, and everyday products
- 160 reviews
- cold-start personas
- metadata for price, spice level, delivery time, portion size, location, tags, popularity score, and average rating

It is not a production dataset. The architecture is designed so larger Yelp/Amazon/Goodreads-style datasets can be loaded later.

## Optional Real Dataset Ingestion: Yelp Open Dataset

The default judge-friendly demo uses the bundled `data/sample/` files. The repository also includes an optional converter for small Yelp Open Dataset subsets. The full Yelp dataset is large and is not bundled or required.

Expected input files:

- `yelp_academic_dataset_business.json`
- `yelp_academic_dataset_review.json`
- `yelp_academic_dataset_user.json` optional

Example:

```bash
python scripts/ingest_yelp_subset.py ^
  --business-file data/raw/yelp/yelp_academic_dataset_business.json ^
  --review-file data/raw/yelp/yelp_academic_dataset_review.json ^
  --user-file data/raw/yelp/yelp_academic_dataset_user.json ^
  --output-dir data/processed/yelp ^
  --max-reviews 5000 ^
  --category-filter Restaurants
```

The script streams JSONL line by line and writes:

- `data/processed/yelp/users.json`
- `data/processed/yelp/items.json`
- `data/processed/yelp/reviews.json`
- `data/processed/yelp/README.md`

Generated Yelp JSON files are ignored by git. To experiment with a processed subset, set `STEWARD_DATA_DIR=data/processed/yelp`. Default startup remains unchanged.

## Reproducibility And Secrets

- No paid API key is required.
- No live database is required.
- `.env.example` contains placeholders only.
- No secrets are committed.
- Deterministic fallback mode runs the full API, tests, and evaluation scripts offline after dependencies are installed.

## Submission Deliverables Checklist

- FastAPI app and `/docs`
- Dockerfile and `docker-compose.yml`
- `.env.example`
- sample data
- tests
- evaluation scripts and result files
- ablation summary
- human evaluation rubric
- demo script: [docs/demo_script.md](docs/demo_script.md)
- sample payloads: [docs/sample_payloads.md](docs/sample_payloads.md)
- solution paper draft: [papers/solution_paper_draft.md](papers/solution_paper_draft.md)
- final checklist: [SUBMISSION_CHECKLIST.md](SUBMISSION_CHECKLIST.md)
