from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


TASK_A_REQUEST = {
    "user_persona": {
        "user_id": "user_001",
        "description": "A Lagos-based university student who likes spicy food, affordable meals, and fast delivery.",
        "past_reviews": [
            {
                "item_name": "Jollof Rice and Chicken",
                "category": "Food",
                "rating": 4,
                "review": "The food was tasty and the portion was fair, but delivery took too long.",
            }
        ],
    },
    "item": {
        "item_id": "item_001",
        "name": "Spicy Chicken Shawarma",
        "category": "Food",
        "price": 2500,
        "metadata": {
            "spicy": True,
            "delivery_time_minutes": 35,
            "portion_size": "medium",
            "location": "Lagos",
        },
    },
}


def test_task_a_returns_rating_review_and_reasoning() -> None:
    response = client.post("/api/task-a/simulate-review", json=TASK_A_REQUEST)

    assert response.status_code == 200
    payload = response.json()
    assert 1 <= payload["predicted_rating"] <= 5
    assert 1 <= payload["predicted_star_rating"] <= 5
    assert payload["generated_review"]
    assert "Spicy Chicken Shawarma" in payload["generated_review"]
    assert "On the details" not in payload["generated_review"]
    forbidden_review_phrases = [
        "target item",
        "stated preferences",
        "user's stated",
        "preference cues",
        "item signals",
        "not just noise",
    ]
    assert not any(phrase in payload["generated_review"].lower() for phrase in forbidden_review_phrases)
    assert 35 <= len(payload["generated_review"].split()) <= 100
    assert payload["behavioural_reasoning_summary"]
    assert payload["user_profile_summary"]
    assert isinstance(payload["positive_signals"], list)
    assert isinstance(payload["negative_signals"], list)
    assert 0 <= payload["confidence"] <= 1


def test_task_a_rating_prediction_stays_between_one_and_five() -> None:
    request = TASK_A_REQUEST.copy()
    request["item"] = {
        "item_id": "item_expensive_slow",
        "name": "Tiny Premium Burger",
        "category": "Food",
        "price": 15000,
        "metadata": {
            "delivery_time_minutes": 95,
            "portion_size": "small",
            "location": "Lagos Island",
        },
    }

    response = client.post("/api/task-a/simulate-review", json=request)

    assert response.status_code == 200
    rating = response.json()["predicted_rating"]
    assert 1 <= rating <= 5


def test_task_a_rejects_placeholder_item_name() -> None:
    response = client.post(
        "/api/task-a/simulate-review",
        json={
            "user_persona": {"user_id": "placeholder", "description": "string", "past_reviews": []},
            "item": {
                "item_id": "placeholder_item",
                "name": "string",
                "category": "string",
                "price": 0,
                "metadata": {},
            },
        },
    )

    assert response.status_code == 422


def test_task_a_sanitises_placeholder_persona_text() -> None:
    response = client.post(
        "/api/task-a/simulate-review",
        json={
            "user_persona": {"user_id": "placeholder", "description": "string", "past_reviews": []},
            "item": {
                "item_id": "item_001",
                "name": "Spicy Chicken Shawarma",
                "category": "Food",
                "price": 2500,
                "metadata": {"spice_level": 4, "delivery_time_minutes": 35, "portion_size": "medium"},
            },
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert "This string" not in payload["generated_review"]
    assert "string" not in payload["generated_review"].lower()
    assert "string" not in payload["user_profile_summary"].lower()
    assert "limited profile evidence" in payload["user_profile_summary"]


def test_task_a_low_rating_has_negative_signals() -> None:
    response = client.post(
        "/api/task-a/simulate-review",
        json={
            "user_persona": {
                "user_id": "strict_budget",
                "description": "A strict budget-conscious user who dislikes expensive meals, slow delivery, and tiny portions.",
                "past_reviews": [
                    {
                        "item_name": "Budget Jollof",
                        "category": "Food",
                        "rating": 2,
                        "review": "It was expensive, late, and the portion was small.",
                    }
                ],
            },
            "item": {
                "item_id": "premium_tiny",
                "name": "Tiny Premium Burger",
                "category": "Food",
                "price": 18000,
                "metadata": {
                    "spice_level": 1,
                    "delivery_time_minutes": 90,
                    "portion_size": "small",
                    "average_rating": 3.0,
                    "popularity_score": 40,
                },
            },
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["predicted_rating"] < 3
    assert payload["negative_signals"]
