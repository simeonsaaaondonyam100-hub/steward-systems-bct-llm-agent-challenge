# Recommendation Ablation Summary

Semantic mode: `tfidf_fallback`
Held-out examples: `21`

| Variant | Hit Rate@5 | Hit Rate@10 | NDCG@5 | NDCG@10 |
|---|---:|---:|---:|---:|
| popularity_baseline | 0.286 | 0.429 | 0.143 | 0.169 |
| content_only_baseline | 0.000 | 0.286 | 0.000 | 0.048 |
| hybrid_without_nigerian_context | 0.286 | 0.571 | 0.121 | 0.194 |
| hybrid_with_nigerian_context | 0.429 | 0.571 | 0.155 | 0.207 |
| hybrid_with_semantic_embeddings_if_available | 0.429 | 0.571 | 0.155 | 0.207 |
| cold_start_only | 0.000 | 0.000 | 0.000 | 0.000 |

The held-out protocol uses early reviews as profile history and later reviews as target relevance labels.
Known training items are removed from the candidate pool before ranking.