# Steward Systems Behavioural Intelligence Agent:
# A Nigerian-Contextualised LLM Agent for Review Simulation and Personalised Recommendation

## Abstract

This paper presents the Steward Systems Behavioural Intelligence Agent, a lightweight and reproducible agentic system for the DSN x BCT LLM Agent Challenge / Data & AI Summit Hackathon 3.0. The system addresses two required tasks: user modelling and review simulation, and personalised recommendation. It is implemented as a FastAPI application with deterministic fallback mode, local sample data, explainable scoring, evaluation scripts, Docker configuration, and optional semantic similarity support. The system is Nigerian-contextualised through a dedicated adapter that interprets affordability, value for money, delivery time, portion size, spice tolerance, local food and drink cues, and mild Nigerian English tone. On the bundled synthetic sample data, Task A achieves RMSE 0.703 and MAE 0.546 for rating prediction. Task B achieves Hit Rate@5 0.429, Hit Rate@10 0.571, NDCG@5 0.155, and NDCG@10 0.207 under a deterministic held-out evaluation. These results are not presented as production-level performance; rather, they show that the architecture is technically sound, explainable, locally runnable, and ready to scale to larger Yelp, Amazon, Goodreads, restaurant, or delivery-platform datasets.

## 1. Introduction

Modern recommendation and review simulation systems should do more than match users to items by broad category. They should model user behaviour: how strict a user is with ratings, what they repeatedly praise, what they complain about, the situations in which they consume items, and the cultural context that shapes their expectations. In a Nigerian setting, the difference between a useful recommendation and a weak one can depend on whether the system understands price sensitivity, Lagos delivery delay, pepper tolerance, portion size, and the practical meaning of "value for money".

The Steward Systems Behavioural Intelligence Agent was built as a competition-grade foundation rather than a full SaaS product. It intentionally avoids external database dependencies, authentication, billing, multi-tenancy, and paid model requirements. The goal is to provide judges with a system they can run from a fresh clone, inspect through API documentation, evaluate with scripts, and understand through transparent reasoning outputs.

The application covers both competition tasks:

- Task A: predict a rating and generate a realistic review from a user persona/history and item details.
- Task B: recommend personalised ranked items from persona, optional history, current context, and candidate metadata.

## 2. Problem Formulation

### Task A: User Modelling / Review Simulation

Given a user persona, optional past reviews, and a target item, the system must predict a star rating from 1 to 5 and generate a written review that is behaviourally faithful. Behavioural fidelity means the output should reflect rating tendency, strictness, preferences, complaints, tone, and contextual expectations.

The Task A output includes:

- `predicted_rating`
- `generated_review`
- `behavioural_reasoning_summary`
- `positive_signals`
- `negative_signals`
- `confidence`
- `user_profile_summary`

### Task B: Personalised Recommendation

Given a user persona, optional past reviews, optional current context, optional category/domain, and `top_k`, the system ranks candidate items. The output must be useful and explainable rather than only a list of item names.

Each recommendation includes:

- rank and item identifiers
- final score
- score breakdown
- reason
- context fit
- preference match explanation
- penalty explanation when applicable
- cold-start note when no past reviews are available

## 3. Data and Preprocessing

The bundled data is synthetic/demo data designed for reproducibility and judge inspection. It is deliberately small enough to run locally and inside Docker.

| Data Type | Count |
|---|---:|
| Users | 18 |
| Items | 60 |
| Reviews | 160 |

The domains include food, drinks, books, movies/entertainment, and everyday products. Food and drinks are the strongest domain because Nigerian contextualisation is a competitive advantage for this challenge.

The dataset includes users with distinct behaviours:

- price-sensitive student
- busy professional
- family-oriented parent
- spice lover
- health-conscious user
- strict reviewer
- generous reviewer
- delivery-sensitive user
- ambience-focused diner
- book/movie preference user
- everyday product buyer
- cold-start users with no history

Items include Nigerian examples such as jollof rice, suya, shawarma, pepper soup, amala, egusi, fried rice, small chops, asun, zobo, Chapman, meat pie, puff-puff, bole, and grilled chicken. Each item has metadata including price, spice level, delivery time, portion size, location, tags, popularity score, and average rating.

For Task B evaluation, the system uses a deterministic held-out split. For each user with enough reviews, earlier reviews become profile history while later reviews become test relevance labels. Items already present in profile history are removed from the candidate pool, which prevents recommending the exact consumed item from the training profile.

The repository also includes optional Yelp Open Dataset ingestion support. Because the full Yelp dataset is large, it is not bundled in the repository. Instead, `scripts/ingest_yelp_subset.py` maps Yelp JSONL business and review files into the same user-item-review schema used by the agent, writing a small processed subset under `data/processed/yelp/` when the user supplies local Yelp files.

## 4. System Architecture

The system is implemented as a Python FastAPI application. API routes are intentionally thin; business logic lives in agents and services.

| Layer | Module(s) | Role |
|---|---|---|
| API | `app/main.py`, `app/api/` | HTTP endpoints and OpenAPI docs |
| Schemas | `app/models/schemas.py` | Pydantic request/response contracts |
| Agents | `app/agents/` | Task orchestration |
| User modelling | `app/services/user_profile_builder.py` | Behavioural profile extraction |
| Nigerian context | `app/services/nigerian_context_adapter.py` | Cultural/contextual scoring |
| Semantics | `app/services/semantic_similarity_service.py` | Optional embeddings and fallback similarity |
| Ranking | `app/services/recommendation_ranking_service.py` | Hybrid recommendation scoring |
| Evaluation | `evaluation/` | Metrics, ablation, human rubric |

The application exposes:

- `GET /`
- `GET /health`
- `POST /api/task-a/simulate-review`
- `POST /api/task-b/recommend`
- `GET /docs`

The default semantic mode is deterministic TF-IDF-style fallback. Optional sentence-transformer support is prepared for `sentence-transformers/all-MiniLM-L6-v2`, but it is disabled by default so the project does not depend on internet access or model downloads at runtime.

## 5. Task A Method

### User Profiling

The user profile builder extracts:

- average rating
- rating strictness
- preferred categories
- category affinity
- positive preference signals
- negative complaint signals
- tone markers
- price sensitivity
- delivery sensitivity
- spice preference
- portion preference
- Nigerian context signals

Profile extraction uses both persona text and past reviews. High-rated reviews contribute preference terms and category affinity, while low-rated reviews contribute complaint and penalty signals.

### Rating Prediction

Rating prediction combines:

- user average rating tendency
- strictness adjustment
- preference overlap with the target item
- category affinity
- item quality/popularity metadata
- price, spice, delivery, and portion fit
- Nigerian context fit
- negative penalties such as high price or slow delivery

The output remains bounded from 1 to 5.

### Review Generation

The review generator is deterministic but varied. It uses controlled templates for:

- short practical tone
- warm enthusiastic tone
- strict reviewer tone
- budget-conscious tone
- delivery-sensitive tone
- family/social tone

Reviews aim for 45-90 words by default. They mention concrete item attributes such as price, delivery time, portion size, spice level, and location. Mild Nigerian English is used only where natural; exaggerated slang is avoided.

## 6. Task B Method

The recommendation agent builds a user profile, loads local candidate items, filters by optional domain if provided, scores candidates, and returns ranked recommendations.

The selected scoring formula is:

```text
final_score =
  0.18 * semantic_similarity
+ 0.38 * preference_match
+ 0.20 * context_match
+ 0.10 * item_quality_or_popularity
+ 0.10 * nigerian_context_match
- 0.04 * penalty
```

These weights were selected through a small, explainable grid search in `scripts/tune_recommendation_weights.py`.

| Component | Meaning |
|---|---|
| Semantic similarity | Similarity between persona/history/context and item text |
| Preference match | Match to extracted user preferences, category affinity, spice, price, and portion needs |
| Context match | Fit to current situation such as dinner, office lunch, family meal, or budget meal |
| Quality/popularity | Sample item metadata score |
| Nigerian context | Price, delivery, portion, pepper, location, and local food/drink fit |
| Penalty | Strong conflicts such as high price for price-sensitive users or slow delivery for delivery-sensitive users |

Cold-start users are handled through persona text, current context, item metadata, and Nigerian-context rules. Cross-domain recommendations are supported because candidate items span food, drinks, books, movies, and everyday products.

## 7. Nigerian Contextualisation Layer

The Nigerian context adapter is a dedicated service rather than scattered hardcoded strings. It interprets:

- affordability and value for money
- price sensitivity
- delivery time and Lagos traffic expectations
- portion size and sharing needs
- pepper/spice preference and mild spice tolerance
- Lagos/mainland/island or broader location cues
- local foods and drinks
- Nigerian English tone

The adapter improves Task A by adjusting ratings and enriching review generation. It improves Task B by contributing `nigerian_context_match` and human-readable explanations. The goal is not gimmickry; it is practical cultural relevance.

## 8. Evaluation

### Task A Metrics

| Metric | Value |
|---|---:|
| Examples | 160 |
| RMSE | 0.703 |
| MAE | 0.546 |
| Average generated review length | 70.9 words |

Task A also writes qualitative review samples to `evaluation/results/task_a_results.json`.

### Task B Metrics

Task B uses held-out later reviews as target relevance labels.

| Metric | Value |
|---|---:|
| Users evaluated | 7 |
| Held-out examples | 21 |
| Hit Rate@5 | 0.429 |
| Hit Rate@10 | 0.571 |
| NDCG@5 | 0.155 |
| NDCG@10 | 0.207 |

### Ablation Comparison

| Variant | HR@5 | HR@10 | NDCG@5 | NDCG@10 |
|---|---:|---:|---:|---:|
| Popularity baseline | 0.286 | 0.429 | 0.143 | 0.169 |
| Content-only baseline | 0.000 | 0.286 | 0.000 | 0.048 |
| Hybrid without Nigerian context | 0.286 | 0.571 | 0.121 | 0.194 |
| Hybrid with Nigerian context | 0.429 | 0.571 | 0.155 | 0.207 |
| Hybrid with semantic embeddings if available | 0.429 | 0.571 | 0.155 | 0.207 |

The sentence-transformer variant currently reports the same metrics because the default runtime uses `tfidf_fallback`. If embeddings are installed and enabled, the same service interface can use sentence-transformer similarity.

### Human Evaluation

The repository includes `evaluation/human_eval_rubric.md` and `evaluation/human_eval_examples.json`. The rubric scores Task A on behavioural fidelity, rating-review consistency, tone realism, item specificity, and Nigerian contextual naturalness. Task B is scored on contextual relevance, usefulness, explanation quality, cold-start quality, cross-domain usefulness, and Nigerian contextual fit.

## 9. Results and Discussion

The Task A RMSE and MAE show that the deterministic rating model can approximate sample ratings while keeping outputs explainable. The generated review length is within a practical range for product/restaurant reviews, and qualitative outputs include concrete details rather than generic praise.

For Task B, the hybrid model outperforms the popularity baseline on Hit Rate@10 and NDCG@10. It also outperforms the hybrid-without-Nigerian-context variant on Hit Rate@5, NDCG@5, and NDCG@10. This suggests that Nigerian contextual signals help place relevant items earlier in the ranking, especially where price, spice, delivery, and portion cues matter.

The absolute NDCG values remain modest. This is expected for a small synthetic dataset with limited behavioural history and sparse held-out relevance labels. The purpose of the evaluation is to demonstrate a realistic, reproducible protocol and show directional value from the hybrid design, not to claim production recommendation accuracy.

## 10. Limitations

The sample data is synthetic and lightweight. It is useful for reproducibility but not a substitute for real transaction, review, or clickstream data. The deterministic review generator is controllable and safe but less expressive than a carefully evaluated LLM generator. The semantic embedding layer is optional and not enabled by default to avoid fragile downloads. The recommendation evaluation uses ratings as implicit relevance labels, which is practical for the hackathon but not as rich as direct user feedback.

The system also does not include a production database, authentication, online learning, or vendor availability signals. These are deliberate scope choices for the competition foundation.

## 11. Future Work

Future improvements include:

- loading larger Yelp, Amazon, Goodreads, or restaurant-delivery datasets
- enabling cached sentence-transformer embeddings
- adding optional LLM generation with strict fallback
- collecting human evaluation scores
- adding freshness, availability, and distance features
- improving train/test protocols with timestamps
- packaging a short demo video and PDF paper export

## 12. Conclusion

The Steward Systems Behavioural Intelligence Agent is a reproducible, explainable, Nigerian-contextualised agent application that solves both required competition tasks. It combines behavioural user profiling, deterministic review simulation, hybrid recommendation scoring, optional semantic similarity, Nigerian context adaptation, evaluation scripts, ablation evidence, and judge-friendly documentation. The project is intentionally lightweight, but its modular architecture is ready for larger datasets and stronger models after the hackathon foundation is accepted.
