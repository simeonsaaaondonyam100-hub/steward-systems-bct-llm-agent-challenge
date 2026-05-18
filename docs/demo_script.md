# Demo Script

This is a 3-5 minute demo flow for a live or recorded presentation.

## 1. Start The Server

```bash
.venv\Scripts\activate
uvicorn app.main:app --reload
```

Narration: "This project runs locally with FastAPI and deterministic fallback mode. No database or paid API key is required."

## 2. Show Health And Docs

Open:

- `http://localhost:8000/health`
- `http://localhost:8000/docs`

Narration: "The API exposes health, Task A review simulation, and Task B recommendation endpoints."

## 3. Run Task A

In `/docs`, open `POST /api/task-a/simulate-review` and use the Task A payload from `docs/sample_payloads.md`.

Explain:

- `predicted_rating`: rating predicted from profile and item signals
- `generated_review`: deterministic human-style review
- `positive_signals`: preference/context matches
- `negative_signals`: delivery, price, portion, or spice risks
- `confidence`: strength of available behavioural evidence
- `user_profile_summary`: inferred rating style and preferences

Suggested narration: "The agent models how this user tends to rate, what they praise or complain about, and how Nigerian-context cues like price, pepper, delivery time, and portion size should affect the review."

## 4. Run Task B

In `/docs`, open `POST /api/task-b/recommend` and use the cold-start Task B payload from `docs/sample_payloads.md`.

Explain:

- ranked recommendations
- `final_score`
- `score_breakdown`
- `context_fit`
- `preference_match_explanation`
- `penalty_explanation`
- `cold_start_note`
- `semantic_mode`

Suggested narration: "Even without past reviews, the system uses persona text, current context, item metadata, and Nigerian-context rules to rank items."

## 5. Show Evaluation

Run:

```bash
python evaluation/evaluate_task_a.py
python evaluation/evaluate_task_b.py
python scripts/tune_recommendation_weights.py
```

Show:

- Task A RMSE/MAE
- Task B Hit Rate/NDCG
- ablation comparison
- `evaluation/results/ablation_summary.md`

## 6. Close With Reproducibility

Open the README and point to:

- Docker instructions
- deterministic fallback mode
- dataset disclosure
- human evaluation rubric
- solution paper draft

Closing line: "The submission is intentionally lightweight, explainable, Nigerian-contextualised, and ready for judges to run from a fresh clone."
