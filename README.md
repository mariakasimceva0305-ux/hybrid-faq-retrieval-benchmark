# Hybrid FAQ Retrieval Benchmark

[Русская версия](#ru) | [English version](#en)

## RU

### О проекте
Benchmark FAQ-поиска: `BM25`, `Dense`, `Hybrid (RRF)` + optional reranking с единым протоколом оценки.

### Гипотезы
1. `Hybrid RRF` даёт лучший баланс точности и устойчивости.
2. Reranking улучшает порядок документов в top-k.
3. Нормализация запроса снижает чувствительность к шумному user input.

### Метрики
`Recall@k`, `MRR@k`, `nDCG@k`, `HitRate@k`, `latency p50/p95`.

## EN

### Overview
A hypothesis-driven FAQ retrieval benchmark to compare BM25, dense retrieval, and hybrid fusion under a consistent offline protocol.
