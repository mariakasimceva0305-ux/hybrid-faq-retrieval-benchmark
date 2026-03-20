from faq_bench.evaluation import hit_rate_at_k, mrr_at_k, ndcg_at_k, recall_at_k


def test_metrics_basic() -> None:
    ranked = ["d2", "d1", "d3"]
    relevant_ids = {"d1"}
    relevant_map = {"d1": 1}

    assert hit_rate_at_k(ranked, relevant_ids, 1) == 0.0
    assert hit_rate_at_k(ranked, relevant_ids, 2) == 1.0
    assert recall_at_k(ranked, relevant_ids, 2) == 1.0
    assert mrr_at_k(ranked, relevant_ids, 3) == 0.5
    assert 0.0 < ndcg_at_k(ranked, relevant_map, 3) <= 1.0
