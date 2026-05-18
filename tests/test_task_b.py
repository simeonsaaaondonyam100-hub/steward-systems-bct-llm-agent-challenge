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
    assert first["context_fit_explanation"]
    assert payload["semantic_mode"]


def test_task_b_scores_are_sorted_descending() -> None:
    response = client.post("/api/task-b/recommend", json=TASK_B_REQUEST)

    assert response.status_code == 200
    scores = [item["score"] for item in response.json()["recommendations"]]
    assert scores == sorted(scores, reverse=True)


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
