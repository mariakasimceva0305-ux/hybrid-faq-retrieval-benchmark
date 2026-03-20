from __future__ import annotations

import math
import re
from collections import Counter, defaultdict

from faq_bench.data import Document
from faq_bench.normalization import normalize_text
from faq_bench.retrievers.base import BaseRetriever, SearchResult

TOKEN_RE = re.compile(r"\w+")


class BM25Retriever(BaseRetriever):
    def __init__(self, documents: list[Document]) -> None:
        self.documents = documents
        self.k1 = 1.5
        self.b = 0.75
        self.tokenized_docs = [self._tokenize(doc.full_text) for doc in documents]
        self.doc_freqs: dict[str, int] = defaultdict(int)
        self.doc_term_counts = [Counter(tokens) for tokens in self.tokenized_docs]
        self.doc_lengths = [len(tokens) for tokens in self.tokenized_docs]
        self.avg_doc_len = sum(self.doc_lengths) / max(len(self.doc_lengths), 1)
        for tokens in self.tokenized_docs:
            for token in set(tokens):
                self.doc_freqs[token] += 1

    def _tokenize(self, text: str) -> list[str]:
        return TOKEN_RE.findall(normalize_text(text))

    def _idf(self, term: str) -> float:
        n = len(self.documents)
        df = self.doc_freqs.get(term, 0)
        return math.log(1 + (n - df + 0.5) / (df + 0.5))

    def _score(self, query_tokens: list[str], index: int) -> float:
        score = 0.0
        term_counts = self.doc_term_counts[index]
        doc_len = self.doc_lengths[index]
        for term in query_tokens:
            if term not in term_counts:
                continue
            tf = term_counts[term]
            idf = self._idf(term)
            numerator = tf * (self.k1 + 1)
            denominator = tf + self.k1 * (1 - self.b + self.b * doc_len / self.avg_doc_len)
            score += idf * numerator / denominator
        return score

    def search(self, query: str, top_k: int) -> list[SearchResult]:
        query_tokens = self._tokenize(query)
        scored: list[SearchResult] = []
        for index, doc in enumerate(self.documents):
            score = self._score(query_tokens, index)
            scored.append(SearchResult(doc_id=doc.doc_id, score=float(score), title=doc.title, text=doc.text))
        scored.sort(key=lambda item: item.score, reverse=True)
        return scored[:top_k]
