import json
from pathlib import Path
import sys

import streamlit as st


ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from app.agents.recommendation_agent import RecommendationAgent  # noqa: E402
from app.agents.review_simulation_agent import ReviewSimulationAgent  # noqa: E402
from app.models.schemas import RecommendRequest, SimulateReviewRequest  # noqa: E402


st.set_page_config(page_title="Steward BCT Agent", layout="wide")
st.title("Steward Systems BCT LLM Agent Challenge")

review_agent = ReviewSimulationAgent()
recommendation_agent = RecommendationAgent()

task_a_tab, task_b_tab = st.tabs(["Simulate Review", "Recommend Items"])

with task_a_tab:
    st.subheader("Task A - Review Simulation")
    default_payload = {
        "user_persona": {
            "user_id": "user_001",
            "description": "A Lagos-based university student who likes spicy food, affordable meals, and fast delivery.",
            "past_reviews": [],
        },
        "item": {
            "item_id": "item_001",
            "name": "Spicy Chicken Shawarma",
            "category": "Food",
            "price": 2500,
            "metadata": {"spicy": True, "delivery_time_minutes": 35, "portion_size": "medium", "location": "Lagos"},
        },
    }
    payload_text = st.text_area("Task A JSON", json.dumps(default_payload, indent=2), height=360)
    if st.button("Simulate Review"):
        response = review_agent.simulate(SimulateReviewRequest(**json.loads(payload_text)))
        st.json(response.model_dump())

with task_b_tab:
    st.subheader("Task B - Recommendation")
    default_payload = {
        "user_persona": {
            "user_id": "user_001",
            "description": "A Lagos-based university student who prefers affordable spicy meals and quick delivery.",
            "past_reviews": [],
        },
        "current_context": "Needs dinner after lectures and wants something filling but not expensive.",
        "top_k": 5,
    }
    payload_text = st.text_area("Task B JSON", json.dumps(default_payload, indent=2), height=320)
    if st.button("Recommend Items"):
        response = recommendation_agent.recommend(RecommendRequest(**json.loads(payload_text)))
        st.json(response.model_dump())
