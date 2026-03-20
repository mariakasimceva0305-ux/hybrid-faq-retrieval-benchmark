from __future__ import annotations

from math import log2
from statistics import median
from typing import Iterable


def hit_rate_at_k(ranked_doc_ids: list[str], relevant_doc_ids: set[str], k: int) -> float:
    return 1.0 if any(doc_id in relevant_doc_ids for doc_id in ranked_doc_ids[:k]) else 0.0


def recall_at_k(ranked_doc_ids: list[str], relevant_doc_ids: set[str], k: int) -> float:
    if not relevant_doc_ids:
        return 0.0
    hits = sum(1 for doc_id in ranked_doc_ids[:k] if doc_id in relevant_doc_ids)
    return hits / len(relevant_doc_ids)


def mrr_at_k(ranked_doc_ids: list[str], relevant_doc_ids: set[str], k: int) -> float:
    for rank, doc_id in enumerate(ranked_doc_ids[:k], start=1):
        if doc_id in relevant_doc_ids:
            return 1.0 / rank
    return 0.0


def ndcg_at_k(ranked_doc_ids: list[str], relevant_map: dict[str, int], k: int) -> float:
    dcg = 0.0
    for i, doc_id in enumerate(ranked_doc_ids[:k], start=1):
        rel = relevant_map.get(doc_id, 0)
        if rel > 0:
            dcg += (2**rel - 1) / log2(i + 1)

    ideal_rels = sorted(relevant_map.values(), reverse=True)[:k]
    idcg = 0.0
    for i, rel in enumerate(ideal_rels, start=1):
        if rel > 0:
            idcg += (2**rel - 1) / log2(i + 1)
    if idcg == 0.0:
        return 0.0
    return dcg / idcg


def summarize_latency_ms(latencies_ms: Iterable[float]) -> dict[str, float]:
    values = sorted(float(x) for x in latencies_ms)
    if not values:
        return {"latency_ms_p50": 0.0, "latency_ms_p95": 0.0}

    def _percentile(p: float) -> float:
        if len(values) == 1:
            return values[0]
        idx = int(round((len(values) - 1) * p))
        return values[idx]

    return {
        "latency_ms_p50": round(_percentile(0.5), 3),
        "latency_ms_p95": round(_percentile(0.95), 3),
    }


def average_metrics(metrics: list[dict[str, float]]) -> dict[str, float]:
    if not metrics:
        return {}
    keys = metrics[0].keys()
    return {key: round(sum(item[key] for item in metrics) / len(metrics), 4) for key in keys}
