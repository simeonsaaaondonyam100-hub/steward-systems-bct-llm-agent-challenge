# Steward Systems Behavioural Intelligence Agent: A Nigerian-Contextualised LLM Agent for Review Simulation and Personalised Recommendation

## 1. Introduction

Introduce the DSN x BCT LLM Agent Challenge problem setting and the need for behavioural intelligence systems that can model user taste, contextual needs, and culturally grounded decision-making. Position the project as a deterministic, reproducible agent foundation that can optionally integrate LLMs later.

## 2. Problem Formulation

Define Task A as conditional review simulation: given user persona/history and an item, predict a rating and generate a faithful written review. Define Task B as contextual recommendation: given persona/history/context, rank candidate items with explanations. Clarify inputs, outputs, assumptions, and cold-start conditions.

## 3. Dataset and Preprocessing

Describe the local sample dataset: Nigerian food, drinks, products, movies, books, 18 users, 60 items, and 160 reviews. Explain metadata fields such as price, spice level, delivery time, portion size, location, tags, average rating, and popularity score. Call out behavioural user types: price-sensitive student, busy professional, family-oriented parent, spice lover, health-conscious user, strict reviewer, generous reviewer, delivery-sensitive user, ambience-focused diner, book/movie user, everyday-product buyer, and cold-start personas. Outline future extension to Yelp, Amazon, Goodreads, restaurant, or delivery-platform datasets.

## 4. System Architecture

Present the FastAPI service, Pydantic schemas, agent orchestration layer, service modules, local JSON data layer, evaluation scripts, Docker runtime, and optional Streamlit demo. Emphasise separation between thin API routes and business logic services. Include a diagram showing: request schema -> agent -> profile builder -> scoring services -> Nigerian context adapter -> structured response.

## 5. Task A: User Modelling and Review Simulation

Explain the behavioural profile builder: average rating, rating strictness, category affinity, positive preference signals, complaint signals, tone markers, price sensitivity level, delivery sensitivity, spice preference, portion-size preference, and Nigerian-context signals. Describe how rating prediction combines user average tendency, preference overlap, category affinity, item quality, negative penalties, strictness adjustment, and Nigerian context fit. Show examples of generated reviews for high, medium, and low predicted ratings.

## 6. Task B: Recommendation Agent

Describe candidate loading, optional category filtering, TF-IDF-style lexical similarity fallback, preference matching, context matching, quality/popularity scoring, Nigerian-context scoring, cold-start handling, sparse-history handling, and cross-domain recommendation. State the ranking formula:

`final_score = 0.30 * semantic_similarity + 0.25 * preference_match + 0.20 * context_match + 0.15 * item_quality_or_popularity + 0.10 * nigerian_context_match`

## 7. Nigerian Contextualisation Layer

Explain how the adapter interprets affordability, value for money, portion size, spice/pepper preference, mild spice tolerance, delivery delays, Lagos traffic sensitivity, mainland/island location cues, group meals, and light Nigerian English tone. Note that Pidgin is used mildly and only where the inferred user tone supports it. Include examples: jollof rice, suya, shawarma, pepper soup, amala, egusi, small chops, asun, zobo, Chapman, meat pie, puff-puff, bole, and grilled chicken.

## 8. Experiments and Ablation Plan

Propose comparisons between baseline average-rating prediction, profile-only scoring, profile plus item metadata, and full Nigerian-context scoring. For recommendation, compare:

1. Popularity/content baseline.
2. Hybrid ranking without Nigerian context.
3. Hybrid ranking with Nigerian context.

Add a short qualitative ablation: inspect whether Nigerian context improves explanations even where numeric metrics are close.

## 9. Evaluation Metrics

Task A: number of examples, RMSE, MAE, generated review length sanity checks, predicted-vs-actual table, qualitative review samples, optional ROUGE/BERTScore hooks, and human behavioural-fidelity evaluation. Task B: Hit Rate@5, Hit Rate@10, NDCG@5, NDCG@10, ablation comparison, and qualitative inspection of recommendation explanations.

## 10. Results Placeholder

Report current sample-data metrics from `evaluation/results/`:

- Task A RMSE and MAE.
- Task B Hit Rate@5, Hit Rate@10, NDCG@5, and NDCG@10.
- Ablation summary for popularity/content baseline, hybrid without Nigerian context, and hybrid with Nigerian context.

Reserve additional tables for human evaluation summaries and example outputs from Nigerian-context cases.

## 11. Limitations

Discuss small sample data, rule-based review generation, limited semantic modelling, no production database, no authentication, and no live learning loop. Frame these as deliberate hackathon-scope choices.

## 12. Future Work

Add larger datasets, optional LLM prompting, embeddings, richer evaluation, online feedback collection, item freshness signals, and deployment hardening only after the competition foundation is accepted.

## 13. Conclusion

Summarise the system as a clear, reproducible behavioural intelligence agent that solves both challenge tasks while demonstrating Nigerian contextual relevance and explainable decision-making.
