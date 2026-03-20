from __future__ import annotations

from collections import defaultdict

from faq_bench.retrievers.base import BaseRetriever, SearchResult


class HybridRRF(BaseRetriever):
    def __init__(self, sparse_retriever: BaseRetriever, dense_retriever: BaseRetriever, rrf_k: int = 60) -> None:
        self.sparse_retriever = sparse_retriever
        self.dense_retriever = dense_retriever
        self.rrf_k = rrf_k

    def search(self, query: str, top_k: int) -> list[SearchResult]:
        sparse = self.sparse_retriever.search(query, top_k=top_k * 2)
        dense = self.dense_retriever.search(query, top_k=top_k * 2)

        scores: dict[str, float] = defaultdict(float)
        metadata: dict[str, SearchResult] = {}

        for rank, result in enumerate(sparse, start=1):
            scores[result.doc_id] += 1.0 / (self.rrf_k + rank)
            metadata[result.doc_id] = result
        for rank, result in enumerate(dense, start=1):
            scores[result.doc_id] += 1.0 / (self.rrf_k + rank)
            metadata[result.doc_id] = result

        merged = [
            SearchResult(
                doc_id=doc_id,
                score=score,
                title=metadata[doc_id].title,
                text=metadata[doc_id].text,
            )
            for doc_id, score in scores.items()
        ]
        merged.sort(key=lambda item: item.score, reverse=True)
        return merged[:top_k]
