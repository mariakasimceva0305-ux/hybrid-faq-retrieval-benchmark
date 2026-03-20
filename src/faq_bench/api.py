from __future__ import annotations

from pathlib import Path
from functools import lru_cache

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from faq_bench.config import load_config
from faq_bench.pipeline import RetrievalPipeline

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CONFIG = ROOT / "configs" / "hybrid.yaml"

app = FastAPI(title="Hybrid FAQ Retrieval Benchmark API")


class SearchRequest(BaseModel):
    query: str = Field(min_length=1)
    top_k: int = Field(default=5, ge=1, le=20)
    config_path: str | None = None


@lru_cache(maxsize=8)
def get_pipeline(config_path: str) -> RetrievalPipeline:
    return RetrievalPipeline(load_config(config_path))


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/search")
def search(request: SearchRequest) -> dict:
    config_path = request.config_path or str(DEFAULT_CONFIG)
    try:
        pipeline = get_pipeline(config_path)
        results = pipeline.search(request.query, top_k=request.top_k)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    return {
        "query": request.query,
        "config_path": config_path,
        "results": [
            {
                "doc_id": item.doc_id,
                "score": round(float(item.score), 4),
                "title": item.title,
                "text": item.text,
            }
            for item in results
        ],
    }
