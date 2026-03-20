from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from faq_bench.config import load_config
from faq_bench.pipeline import RetrievalPipeline

CONFIGS = [
    ROOT / "configs" / "bm25.yaml",
    ROOT / "configs" / "dense.yaml",
    ROOT / "configs" / "hybrid.yaml",
]


def main() -> None:
    rows = []
    for config_path in CONFIGS:
        config = load_config(config_path)
        pipeline = RetrievalPipeline(config)
        artifacts = pipeline.run_benchmark()
        rows.append(artifacts.summary)

    out_path = ROOT / "reports" / "comparison.json"
    out_path.write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Written {out_path}")


if __name__ == "__main__":
    main()
