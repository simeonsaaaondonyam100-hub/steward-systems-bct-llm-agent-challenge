# Sample Payloads

## Task A Request

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
      "location": "Lagos",
      "tags": ["shawarma", "spicy", "quick"]
    }
  }
}
```

## Task A Expected Response Shape

```json
{
  "predicted_rating": 5.0,
  "generated_review": "The generated review text appears here.",
  "behavioural_reasoning_summary": "Reasoning summary appears here.",
  "positive_signals": ["signal"],
  "negative_signals": [],
  "confidence": 0.68,
  "user_profile_summary": "profile summary appears here"
}
```

## Task B Request

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

## Task B Expected Response Shape

```json
{
  "recommendations": [
    {
      "rank": 1,
      "item_id": "item_001",
      "item_name": "Spicy Chicken Shawarma",
      "name": "Spicy Chicken Shawarma",
      "category": "Food",
      "final_score": 0.46,
      "score": 0.46,
      "score_breakdown": {
        "semantic_similarity": 0.13,
        "preference_match": 0.81,
        "context_match": 0.22,
        "item_quality_or_popularity": 0.82,
        "nigerian_context_match": 1.0,
        "penalty": 0.0
      },
      "reason": "Ranking explanation appears here.",
      "context_fit": "Context fit explanation appears here.",
      "context_fit_explanation": "Context fit explanation appears here.",
      "preference_match_explanation": "Preference explanation appears here.",
      "penalty_explanation": null,
      "cold_start_note": "Cold-start note appears here when applicable.",
      "metadata": {}
    }
  ],
  "profile_summary": "profile summary appears here",
  "cold_start_note": "cold-start note appears here",
  "ranking_formula": "final_score = ...",
  "semantic_mode": "tfidf_fallback"
}
```

## Cold-Start Recommendation Request

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

## Cross-Domain Recommendation Request

```json
{
  "user_persona": {
    "user_id": "weekend_reader",
    "description": "Book and movie lover who enjoys Nigerian stories, zobo or Chapman with snacks, and calm weekend plans.",
    "past_reviews": []
  },
  "current_context": "Wants a relaxed weekend plan at home with something to read or watch and a drink.",
  "top_k": 6
}
```
