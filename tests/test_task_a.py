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
    assert payload["generated_review"]
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
