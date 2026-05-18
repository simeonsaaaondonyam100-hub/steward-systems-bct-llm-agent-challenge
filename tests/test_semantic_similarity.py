from app.services.semantic_similarity_service import SemanticSimilarityService


def test_semantic_similarity_service_falls_back_without_required_model() -> None:
    service = SemanticSimilarityService(enable_sentence_transformers=False)
    service.fit_or_load_corpus(
        [
            {"item_id": "a", "text": "spicy jollof rice with chicken"},
            {"item_id": "b", "text": "durable rechargeable standing fan"},
        ]
    )

    scores = service.batch_similarity("peppery rice dinner", ["spicy jollof rice", "standing fan"])

    assert service.mode == "tfidf_fallback"
    assert len(scores) == 2
    assert scores[0] > scores[1]
