from __future__ import annotations

from faq_bench.normalization import normalize_text
from faq_bench.retrievers.base import SearchResult


class CrossEncoderReranker:
    def __init__(self, model_name: str) -> None:
        self.model_name = model_name
        self.mode = "lexical-fallback"
        self._model = None
        try:
            from sentence_transformers import CrossEncoder

            self._model = CrossEncoder(model_name)
            self.mode = "cross-encoder"
        except Exception:
            self._model = None

    def _fallback_score(self, query: str, result: SearchResult) -> float:
        q = set(normalize_text(query).split())
        d = set(normalize_text(f"{result.title} {result.text}").split())
        overlap = len(q & d)
        return float(overlap) + result.score

    def rerank(self, query: str, results: list[SearchResult], top_n: int) -> list[SearchResult]:
        head = results[:top_n]
        tail = results[top_n:]
        if not head:
            return results

        if self._model is not None:
            pairs = [(query, f"{item.title}. {item.text}") for item in head]
            scores = self._model.predict(pairs)
            reranked = [
                SearchResult(doc_id=item.doc_id, score=float(score), title=item.title, text=item.text)
                for item, score in zip(head, scores)
            ]
        else:
            reranked = [
                SearchResult(
                    doc_id=item.doc_id,
                    score=self._fallback_score(query, item),
                    title=item.title,
                    text=item.text,
                )
                for item in head
            ]
        reranked.sort(key=lambda item: item.score, reverse=True)
        return reranked + tail
