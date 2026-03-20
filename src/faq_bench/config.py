from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml


@dataclass(slots=True)
class BenchmarkConfig:
    experiment_name: str
    corpus_path: str
    queries_path: str
    qrels_path: str
    retriever_type: str
    use_query_normalization: bool = True
    use_reranker: bool = False
    dense_model_name: str = "sentence-transformers/all-MiniLM-L6-v2"
    reranker_model_name: str = "cross-encoder/ms-marco-MiniLM-L-6-v2"
    top_k: int = 5
    rerank_top_n: int = 5
    rrf_k: int = 60

    def resolve_paths(self, root: Path) -> "BenchmarkConfig":
        def _resolve(path_str: str) -> str:
            path = Path(path_str)
            if path.is_absolute():
                return str(path)
            return str((root / path).resolve())

        return BenchmarkConfig(
            experiment_name=self.experiment_name,
            corpus_path=_resolve(self.corpus_path),
            queries_path=_resolve(self.queries_path),
            qrels_path=_resolve(self.qrels_path),
            retriever_type=self.retriever_type,
            use_query_normalization=self.use_query_normalization,
            use_reranker=self.use_reranker,
            dense_model_name=self.dense_model_name,
            reranker_model_name=self.reranker_model_name,
            top_k=self.top_k,
            rerank_top_n=self.rerank_top_n,
            rrf_k=self.rrf_k,
        )


def load_config(config_path: str | Path) -> BenchmarkConfig:
    config_path = Path(config_path).resolve()
    with config_path.open("r", encoding="utf-8") as f:
        payload: dict[str, Any] = yaml.safe_load(f)
    cfg = BenchmarkConfig(**payload)
    root = config_path.parents[1]
    return cfg.resolve_paths(root)
