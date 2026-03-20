from __future__ import annotations

import json
import urllib.request

payload = {
    "query": "How do I reset my password?",
    "top_k": 3,
    "config_path": "configs/hybrid.yaml",
}

req = urllib.request.Request(
    "http://127.0.0.1:8000/search",
    data=json.dumps(payload).encode("utf-8"),
    headers={"Content-Type": "application/json"},
    method="POST",
)

with urllib.request.urlopen(req) as response:
    print(response.read().decode("utf-8"))
