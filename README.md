# Hybrid FAQ Retrieval Benchmark

Гипотезно-ориентированный benchmark для FAQ-поиска: BM25, dense retrieval, hybrid fusion, optional reranking, офлайн-оценка и FastAPI serving.

## Кратко

Проект решает задачу поиска наиболее релевантного ответа по корпусу FAQ-документов. В репозитории есть:

- воспроизводимый локальный benchmark;
- несколько retrieval-режимов: `bm25`, `dense`, `hybrid_rrf`;
- optional reranking для топ-кандидатов;
- offline-метрики качества;
- demo-корпус и готовые запросы;
- API для локального serving.

## Какие гипотезы проверяет проект

1. **Hybrid retrieval** (BM25 + dense + RRF) даёт более устойчивое качество, чем любой отдельный retriever.
2. **Reranking** улучшает ранжирование внутри top-k кандидатов.
3. **Query normalization** помогает на шумных пользовательских запросах.
4. Одинаковая экспериментальная обвязка позволяет сравнивать retrieval-конфигурации без ручной рутины.

## Что делает система

Система:

- читает локальный корпус FAQ из `jsonl`;
- готовит документы и запросы;
- строит sparse/dense представления;
- выполняет retrieval;
- опционально делает reranking;
- считает offline-метрики;
- сохраняет отчёт и артефакты прогона;
- поднимает API для поиска по корпусу.

## Retrieval pipeline

1. **Load corpus**: загрузка FAQ-документов и qrels.
2. **Normalize**: базовая нормализация текста и запросов.
3. **Retrieve**:
   - `bm25`: лексический baseline;
   - `dense`: эмбеддинги + cosine similarity;
   - `hybrid_rrf`: reciprocal rank fusion для sparse+dense.
4. **Rerank (optional)**: дополнительное ранжирование top-n кандидатов.
5. **Evaluate**: `Recall@k`, `MRR@k`, `nDCG@k`, `HitRate@k`, latency.
6. **Report**: JSON summary + Markdown summary.

## Поддерживаемые режимы

### BM25
Минимальный и быстрый baseline для keyword-heavy запросов.

### Dense
Семантический retriever на базе `sentence-transformers`.

### Hybrid RRF
Сливает sparse и dense сигналы через reciprocal rank fusion.

### Reranking
Дополнительный этап ранжирования поверх top-k кандидатов. По умолчанию используется cross-encoder, при недоступности модели — lexical fallback.

## Demo-корпус

В репозитории есть встроенный FAQ-корпус:

- путь: `data/demo_faq/`
- домен: support / billing / security / access
- формат: `corpus.jsonl`, `queries.jsonl`, `qrels.tsv`

Это позволяет:

- проверить пайплайн локально без внешних данных;
- сравнить retrieval-конфигурации на одном и том же наборе;
- быстро убедиться, что проект запускается end-to-end.

## Структура репозитория

```text
configs/                   # YAML-конфиги экспериментов
data/demo_faq/             # встроенный demo-корпус
examples/                  # примеры запросов и сценариев
reports/                   # результаты benchmark-запусков
scripts/                   # CLI-скрипты
src/faq_bench/             # core-логика benchmark-а
tests/                     # smoke/unit tests
PROJECT_SPEC.md            # спецификация проекта
CURSOR_PROMPT.txt          # промпт для Cursor
Dockerfile                 # контейнеризация
Makefile                   # быстрые команды
```

## Как запустить

### 1. Установка

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Для Windows:

```powershell
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Benchmark на demo-датасете

```bash
python scripts/run_benchmark.py --config configs/hybrid.yaml
```

### 3. Сравнение всех конфигураций

```bash
python scripts/run_benchmark.py --config configs/bm25.yaml
python scripts/run_benchmark.py --config configs/dense.yaml
python scripts/run_benchmark.py --config configs/hybrid.yaml
```

### 4. API

```bash
uvicorn faq_bench.api:app --reload
```

Эндпоинты:

- `GET /health`
- `POST /search`

Пример тела запроса:

```json
{
  "query": "How can I restore access to my account?",
  "top_k": 5,
  "config_path": "configs/hybrid.yaml"
}
```

## Метрики

В benchmark входят:

- `Recall@k`
- `MRR@k`
- `nDCG@k`
- `HitRate@k`
- `latency_ms_p50`
- `latency_ms_p95`

Результаты сохраняются в:

- `reports/latest_summary.json`
- `reports/latest_run_details.json`
- `reports/latest_summary.md`

## Текущий scope

- Dense retrieval и reranking зависят от внешних моделей из `sentence-transformers`.
- Demo-корпус небольшой и нужен для воспроизводимого smoke/eval прогона.
- Для прикладного использования проект рассчитан на замену demo-корпуса на свой FAQ или help-center корпус.

## Что можно улучшать дальше

- hard-negative mining и fine-tuning dense retriever;
- language-aware normalization для multilingual FAQ;
- online A/B-проверка search quality;
- экспорт экспериментов в MLflow или Weights & Biases;
- кэширование эмбеддингов и инкрементальное обновление индекса.
