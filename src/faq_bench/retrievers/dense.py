from __future__ import annotations

import math
from collections import Counter

import numpy as np

from faq_bench.data import Document
from faq_bench.normalization import normalize_text
from faq_bench.retrievers.base import BaseRetriever, SearchResult


class DenseRetriever(BaseRetriever):
    def __init__(self, documents: list[Document], model_name: str) -> None:
        self.documents = documents
        self.model_name = model_name
        self.mode = "tfidf-fallback"
        self._dense_model = None
        self._doc_embeddings = None
        try:
            from sentence_transformers import SentenceTransformer

            self._dense_model = SentenceTransformer(model_name)
            self._doc_embeddings = self._dense_model.encode(
                [doc.full_text for doc in documents],
                normalize_embeddings=True,
                convert_to_numpy=True,
            )
            self.mode = "sentence-transformers"
        except Exception:
            self._fallback_vocab = self._build_vocab()
            self._doc_embeddings = self._compute_fallback_doc_vectors()

    def _build_vocab(self) -> dict[str, int]:
        vocab: dict[str, int] = {}
        for doc in self.documents:
            for token in normalize_text(doc.full_text).split():
                if token not in vocab:
                    vocab[token] = len(vocab)
        return vocab

    def _vectorize(self, text: str) -> np.ndarray:
        vector = np.zeros(len(self._fallback_vocab), dtype=np.float32)
        counts = Counter(normalize_text(text).split())
        for token, count in counts.items():
            index = self._fallback_vocab.get(token)
            if index is not None:
                vector[index] = float(count)
        norm = np.linalg.norm(vector)
        if norm > 0:
            vector /= norm
        return vector

    def _compute_fallback_doc_vectors(self) -> np.ndarray:
        return np.stack([self._vectorize(doc.full_text) for doc in self.documents])

    def _encode_query(self, query: str) -> np.ndarray:
        if self._dense_model is not None:
            return self._dense_model.encode(query, normalize_embeddings=True, convert_to_numpy=True)
        return self._vectorize(query)

    def search(self, query: str, top_k: int) -> list[SearchResult]:
        query_embedding = self._encode_query(query)
        scores = np.dot(self._doc_embeddings, query_embedding)
        order = np.argsort(scores)[::-1][:top_k]
        results: list[SearchResult] = []
        for idx in order:
            doc = self.documents[int(idx)]
            results.append(SearchResult(doc_id=doc.doc_id, score=float(scores[idx]), title=doc.title, text=doc.text))
        return results
