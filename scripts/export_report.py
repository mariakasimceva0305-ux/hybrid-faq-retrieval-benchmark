from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
summary_path = ROOT / "reports" / "latest_summary.json"
markdown_path = ROOT / "reports" / "latest_summary.md"

if not summary_path.exists():
    raise SystemExit("Run the benchmark first: reports/latest_summary.json not found")

summary = json.loads(summary_path.read_text(encoding="utf-8"))
lines = ["# Benchmark Summary", ""]
for key, value in summary.items():
    lines.append(f"- {key}: {value}")
lines.append("")
markdown_path.write_text("\n".join(lines), encoding="utf-8")
print(f"Written {markdown_path}")
