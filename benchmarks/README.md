# 🚀 PyDataUI vs FastAPI Benchmarks

This directory contains benchmark implementations and automated runner for comparing **PyDataUI (`pyrustapi`)** against **FastAPI (`uvicorn + uvloop`)**.

## Files

- `pydataui_app.py`: PyDataUI benchmark server exposing `/sync-get`, `/async-get`, `/sync-post`, `/async-post`.
- `fastapi_app.py`: FastAPI benchmark server exposing identical endpoints and data models.
- `run_benchmark.py`: Benchmark harness utilizing ApacheBench (`ab`) to run warmups, execute loads, measure percentiles, and generate JSON/Markdown reports.
- `benchmark_results.json`: Raw results from latest benchmark runs.

## Running the Benchmark

```bash
# Default run (2000 requests, 50 concurrency)
python benchmarks/run_benchmark.py

# Custom load
python benchmarks/run_benchmark.py --requests 5000 --concurrency 100
```

For full analysis and methodology, see [docs/BENCHMARKS.md](../docs/BENCHMARKS.md).
