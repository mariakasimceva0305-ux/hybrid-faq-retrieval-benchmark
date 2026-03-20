from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass(slots=True)
class SearchResult:
    doc_id: str
    score: float
    title: str
    text: str


class BaseRetriever(ABC):
    @abstractmethod
    def search(self, query: str, top_k: int) -> list[SearchResult]:
        raise NotImplementedError
