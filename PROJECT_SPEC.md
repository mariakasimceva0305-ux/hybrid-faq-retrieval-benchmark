# Project Specification

## Name
Hybrid FAQ Retrieval Benchmark

## Goal
Build a reproducible retrieval benchmark for FAQ search that compares sparse, dense and hybrid retrieval strategies under a shared evaluation protocol.

## Positioning
This repository is an applied NLP / IR systems project focused on controlled offline evaluation rather than a full RAG product. The emphasis is on retrieval quality, reranking and hypothesis-driven experimentation.

## Core capabilities
- Local benchmark runner
- BM25 retriever
- Dense embedding retriever
- Hybrid RRF retriever
- Optional reranking stage
- Query normalization
- Offline metrics and experiment reports
- FastAPI serving endpoint
- Demo corpus for smoke tests

## Main hypotheses
- H1: Hybrid retrieval improves robustness across lexical and semantic query variants.
- H2: Reranking improves top-k ordering quality.
- H3: Query normalization improves retrieval on noisy or underspecified queries.
- H4: A shared config-driven pipeline makes retrieval comparisons reproducible.

## Data contract
### corpus.jsonl
Each line:
```json
{"doc_id": "faq_001", "title": "...", "text": "...", "category": "security"}
```

### queries.jsonl
Each line:
```json
{"query_id": "q_001", "text": "How do I reset my password?"}
```

### qrels.tsv
Tab-separated columns:
```text
query_id\tdoc_id\trelevance
```

## Experiment outputs
- reports/latest_summary.json
- reports/latest_run_details.json
- reports/latest_summary.md

## Success criteria
- End-to-end benchmark works on demo data
- Multiple configs can be compared without code changes
- Metrics are computed deterministically
- API reuses the same retrieval components as offline benchmark

## Non-goals
- No online learning loop in v1
- No production infra requirements
- No GPU-only implementation assumptions
