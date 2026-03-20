PYTHON=python

install:
	$(PYTHON) -m pip install -r requirements.txt

benchmark-bm25:
	$(PYTHON) scripts/run_benchmark.py --config configs/bm25.yaml

benchmark-dense:
	$(PYTHON) scripts/run_benchmark.py --config configs/dense.yaml

benchmark-hybrid:
	$(PYTHON) scripts/run_benchmark.py --config configs/hybrid.yaml

serve:
	uvicorn faq_bench.api:app --reload

test:
	$(PYTHON) -m pytest tests -q
