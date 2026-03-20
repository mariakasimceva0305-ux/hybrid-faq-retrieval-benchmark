from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path


@dataclass(slots=True)
class Document:
    doc_id: str
    title: str
    text: str
    category: str | None = None

    @property
    def full_text(self) -> str:
        if self.title:
            return f"{self.title}. {self.text}"
        return self.text


@dataclass(slots=True)
class Query:
    query_id: str
    text: str


def load_corpus(path: str | Path) -> list[Document]:
    path = Path(path)
    documents: list[Document] = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            row = json.loads(line)
            documents.append(
                Document(
                    doc_id=row["doc_id"],
                    title=row.get("title", ""),
                    text=row["text"],
                    category=row.get("category"),
                )
            )
    return documents


def load_queries(path: str | Path) -> list[Query]:
    path = Path(path)
    queries: list[Query] = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            row = json.loads(line)
            queries.append(Query(query_id=row["query_id"], text=row["text"]))
    return queries


def load_qrels(path: str | Path) -> dict[str, dict[str, int]]:
    path = Path(path)
    qrels: dict[str, dict[str, int]] = {}
    with path.open("r", encoding="utf-8") as f:
        header = next(f, None)
        if header is None:
            return qrels
        for line in f:
            if not line.strip():
                continue
            query_id, doc_id, relevance_str = line.rstrip("\n").split("\t")
            qrels.setdefault(query_id, {})[doc_id] = int(relevance_str)
    return qrels
