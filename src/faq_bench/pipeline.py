from __future__ import annotations

import json
import time
from dataclasses import asdict, dataclass
from pathlib import Path

from faq_bench.config import BenchmarkConfig
from faq_bench.data import Document, Query, load_corpus, load_qrels, load_queries
from faq_bench.evaluation import average_metrics, hit_rate_at_k, mrr_at_k, ndcg_at_k, recall_at_k, summarize_latency_ms
from faq_bench.normalization import normalize_text
from faq_bench.rerankers.cross_encoder import CrossEncoderReranker
from faq_bench.retrievers.base import BaseRetriever, SearchResult
from faq_bench.retrievers.bm25 import BM25Retriever
from faq_bench.retrievers.dense import DenseRetriever
from faq_bench.retrievers.hybrid import HybridRRF


@dataclass(slots=True)
class BenchmarkArtifacts:
    summary: dict
    run_details: dict


class RetrievalPipeline:
    def __init__(self, config: BenchmarkConfig) -> None:
        self.config = config
        self.documents = load_corpus(config.corpus_path)
        self.queries = load_queries(config.queries_path)
        self.qrels = load_qrels(config.qrels_path)
        self.retriever = self._build_retriever()
        self.reranker = CrossEncoderReranker(config.reranker_model_name) if config.use_reranker else None

    def _build_retriever(self) -> BaseRetriever:
        if self.config.retriever_type == "bm25":
            return BM25Retriever(self.documents)
        if self.config.retriever_type == "dense":
            return DenseRetriever(self.documents, self.config.dense_model_name)
        if self.config.retriever_type == "hybrid_rrf":
            sparse = BM25Retriever(self.documents)
            dense = DenseRetriever(self.documents, self.config.dense_model_name)
            return HybridRRF(sparse, dense, rrf_k=self.config.rrf_k)
        raise ValueError(f"Unsupported retriever_type: {self.config.retriever_type}")

    def search(self, query: str, top_k: int | None = None) -> list[SearchResult]:
        top_k = top_k or self.config.top_k
        prepared_query = normalize_text(query) if self.config.use_query_normalization else query
        results = self.retriever.search(prepared_query, top_k=top_k)
        if self.reranker is not None:
            results = self.reranker.rerank(prepared_query, results, top_n=min(self.config.rerank_top_n, len(results)))
        return results[:top_k]

    def run_benchmark(self) -> BenchmarkArtifacts:
        per_query_metrics: list[dict[str, float]] = []
        latencies_ms: list[float] = []
        examples: list[dict] = []

        for query in self.queries:
            start = time.perf_counter()
            results = self.search(query.text, top_k=self.config.top_k)
            latency_ms = (time.perf_counter() - start) * 1000.0
            latencies_ms.append(latency_ms)

            relevant_map = self.qrels.get(query.query_id, {})
            relevant_ids = set(relevant_map.keys())
            ranked_ids = [item.doc_id for item in results]
            metrics = {
                f"Recall@{self.config.top_k}": recall_at_k(ranked_ids, relevant_ids, self.config.top_k),
                f"MRR@{self.config.top_k}": mrr_at_k(ranked_ids, relevant_ids, self.config.top_k),
                f"nDCG@{self.config.top_k}": ndcg_at_k(ranked_ids, relevant_map, self.config.top_k),
                f"HitRate@{self.config.top_k}": hit_rate_at_k(ranked_ids, relevant_ids, self.config.top_k),
            }
            per_query_metrics.append(metrics)
            examples.append(
                {
                    "query_id": query.query_id,
                    "query": query.text,
                    "ranked_doc_ids": ranked_ids,
                    "top_hit": results[0].doc_id if results else None,
                    "relevant_doc_ids": list(relevant_ids),
                    "latency_ms": round(latency_ms, 3),
                }
            )

        aggregated = average_metrics(per_query_metrics)
        aggregated.update(summarize_latency_ms(latencies_ms))
        aggregated.update(
            {
                "experiment_name": self.config.experiment_name,
                "retriever_type": self.config.retriever_type,
                "use_reranker": self.config.use_reranker,
                "num_queries": len(self.queries),
                "num_documents": len(self.documents),
            }
        )
        run_details = {
            "config": asdict(self.config),
            "query_examples": examples,
            "reranker_mode": getattr(self.reranker, "mode", None),
            "retriever_backend": getattr(self.retriever, "mode", self.config.retriever_type),
        }
        return BenchmarkArtifacts(summary=aggregated, run_details=run_details)


def save_artifacts(artifacts: BenchmarkArtifacts, reports_dir: str | Path) -> None:
    reports_dir = Path(reports_dir)
    reports_dir.mkdir(parents=True, exist_ok=True)
    summary_path = reports_dir / "latest_summary.json"
    details_path = reports_dir / "latest_run_details.json"
    markdown_path = reports_dir / "latest_summary.md"

    summary_path.write_text(json.dumps(artifacts.summary, ensure_ascii=False, indent=2), encoding="utf-8")
    details_path.write_text(json.dumps(artifacts.run_details, ensure_ascii=False, indent=2), encoding="utf-8")

    markdown = [
        f"# {artifacts.summary['experiment_name']}",
        "",
        f"- retriever_type: {artifacts.summary['retriever_type']}",
        f"- use_reranker: {artifacts.summary['use_reranker']}",
        f"- num_queries: {artifacts.summary['num_queries']}",
        f"- num_documents: {artifacts.summary['num_documents']}",
        "",
        "## Metrics",
        "",
    ]
    for key, value in artifacts.summary.items():
        if key in {"experiment_name", "retriever_type", "use_reranker", "num_queries", "num_documents"}:
            continue
        markdown.append(f"- {key}: {value}")
    markdown.append("")
    markdown_path.write_text("\n".join(markdown), encoding="utf-8")
