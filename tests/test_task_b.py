from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


TASK_B_REQUEST = {
    "user_persona": {
        "user_id": "user_001",
        "description": "A Lagos-based university student who prefers affordable spicy meals and quick delivery.",
        "past_reviews": [],
    },
    "current_context": "Needs dinner after lectures and wants something filling but not expensive.",
    "top_k": 5,
}


def test_task_b_returns_ranked_recommendations() -> None:
    response = client.post("/api/task-b/recommend", json=TASK_B_REQUEST)

    assert response.status_code == 200
    payload = response.json()
    assert len(payload["recommendations"]) == 5
    assert payload["profile_summary"]
    assert payload["cold_start_note"]

    first = payload["recommendations"][0]
    assert first["item_id"]
    assert first["name"]
    assert first["item_name"] == first["name"]
    assert 0 <= first["score"] <= 1
    assert first["final_score"] == first["score"]
    assert first["score_breakdown"]
    assert "penalty" in first["score_breakdown"]
    assert first["context_fit"]
    assert first["preference_match_explanation"]
    assert "penalty_explanation" in first
    assert "cold_start_note" in first
    assert first["reason"]
    assert not first["reason"].startswith("Breakdown:")
    assert "Breakdown:" not in first["reason"]
    assert first["context_fit_explanation"]
    assert payload["semantic_mode"]


def test_task_b_scores_are_sorted_descending() -> None:
    response = client.post("/api/task-b/recommend", json=TASK_B_REQUEST)

    assert response.status_code == 200
    scores = [item["score"] for item in response.json()["recommendations"]]
    assert scores == sorted(scores, reverse=True)


def test_task_b_valid_food_context_returns_food_recommendations() -> None:
    response = client.post(
        "/api/task-b/recommend",
        json={
            "user_persona": {
                "user_id": "user_002",
                "description": "A Lagos-based university student who likes spicy food, affordable meals, filling portions, and quick delivery. He dislikes expensive meals with small portions and slow delivery.",
                "past_reviews": [
                    {
                        "item_name": "Suya Platter",
                        "category": "Food",
                        "rating": 5,
                        "review": "Fresh, spicy, affordable, and very satisfying. The pepper was just right and the portion was worth the price.",
                    },
                    {
                        "item_name": "Burger Meal",
                        "category": "Food",
                        "rating": 2,
                        "review": "Too expensive for the portion. Delivery was slow and the food was already cold when it arrived.",
                    },
                    {
                        "item_name": "Jollof Rice and Chicken",
                        "category": "Food",
                        "rating": 4,
                        "review": "The jollof had good smoky flavour and the chicken was tasty. The portion was fair for the price.",
                    },
                ],
            },
            "current_context": "Needs dinner after lectures and wants something filling, spicy, affordable, and not too slow to deliver.",
            "candidate_domain": "Food",
            "top_k": 5,
        },
    )

    assert response.status_code == 200
    recommendations = response.json()["recommendations"]
    assert len(recommendations) == 5
    assert all(item["category"] == "Food" for item in recommendations)
    assert all(item["reason"] and "Breakdown:" not in item["reason"] for item in recommendations)
    assert all(item["score_breakdown"] for item in recommendations)
    assert "Personal history mode used" in response.json()["cold_start_note"]


def test_task_b_cold_start_request_returns_recommendations() -> None:
    response = client.post(
        "/api/task-b/recommend",
        json={
            "user_persona": {
                "user_id": "cold_test",
                "description": "Cold-start Lagos visitor who wants affordable local food, not too much pepper, and quick delivery.",
                "past_reviews": [],
            },
            "current_context": "Needs a light dinner near Yaba after a long day.",
            "top_k": 3,
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert len(payload["recommendations"]) == 3
    assert "Cold-start" in payload["cold_start_note"]
    assert all(item["cold_start_note"] for item in payload["recommendations"])


def test_task_b_placeholder_persona_has_honest_cold_start_explanations() -> None:
    response = client.post(
        "/api/task-b/recommend",
        json={
            "user_persona": {
                "user_id": "placeholder",
                "description": "string",
                "past_reviews": [
                    {
                        "item_name": "string",
                        "category": "string",
                        "rating": 5,
                        "review": "string",
                    }
                ],
            },
            "current_context": "string",
            "candidate_domain": "string",
            "top_k": 3,
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert "Cold-start" in payload["cold_start_note"]
    assert (
        payload["cold_start_note"]
        == "Cold-start mode used: placeholder or insufficient profile history was ignored, so recommendations are based on broad popularity, item quality, and Nigerian-context fit."
    )
    assert "Personal history mode used" not in payload["cold_start_note"]
    assert "limited profile evidence" in payload["profile_summary"]
    assert "string" not in payload["profile_summary"].lower()
    for recommendation in payload["recommendations"]:
        assert "semantic/text similarity" not in recommendation["context_fit"]
        assert "cold-start popularity and broad Nigerian-context fit" in recommendation["context_fit"]
        assert recommendation["cold_start_note"] == payload["cold_start_note"]


def test_task_b_book_and_product_reasons_do_not_use_portion_language() -> None:
    for category in ["Book", "Product"]:
        response = client.post(
            "/api/task-b/recommend",
            json={
                "user_persona": {
                    "user_id": f"{category.lower()}_user",
                    "description": f"A Lagos reader and shopper looking for reliable {category.lower()} options with good quality signals.",
                    "past_reviews": [],
                },
                "current_context": f"Wants a useful {category.lower()} recommendation with strong quality signals.",
                "candidate_domain": category,
                "top_k": 3,
            },
        )

        assert response.status_code == 200
        recommendations = response.json()["recommendations"]
        assert recommendations
        assert all(item["category"] == category for item in recommendations)
        assert all("portion" not in item["reason"].lower() for item in recommendations)
