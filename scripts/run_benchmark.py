from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from faq_bench.config import load_config
from faq_bench.pipeline import RetrievalPipeline, save_artifacts


def main() -> None:
    parser = argparse.ArgumentParser(description="Run FAQ retrieval benchmark")
    parser.add_argument("--config", required=True, help="Path to YAML config")
    args = parser.parse_args()

    config = load_config(args.config)
    pipeline = RetrievalPipeline(config)
    artifacts = pipeline.run_benchmark()
    save_artifacts(artifacts, reports_dir=ROOT / "reports")

    print("Benchmark completed")
    for key, value in artifacts.summary.items():
        print(f"{key}: {value}")


if __name__ == "__main__":
    main()
