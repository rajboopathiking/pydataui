# ⚡ Performance Benchmarks: PyDataUI (PyRustAPI) vs FastAPI (Uvicorn)

This benchmark suite provides a rigorous, head-to-head comparison between **PyDataUI** (powered by the Rust `pyrustapi` engine on Tokio/Hyper) and **FastAPI** (running on `uvicorn` with `uvloop`).

All tests measure real HTTP performance over loopback TCP sockets using **ApacheBench (`ab`)**, evaluating both **Real GET** (payload serialization) and **Real POST** (Pydantic model validation and serialization) on a local development machine.

---

## 📊 Executive Summary (Local Machine Measured Results)

### Profile A: High-Concurrency Stress Test (c=100, 5,000 requests)

Under extreme concurrency (`100 concurrent workers`), PyDataUI demonstrates resilience and stability, while FastAPI/Uvicorn suffers severe queuing contention on asynchronous POST:

| Benchmark Workload | PyDataUI (`pyrustapi`) | FastAPI (`uvicorn + uvloop`) | Speedup Advantage | PyDataUI Latency (Mean) | FastAPI Latency (Mean) |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Real POST (Async Pydantic)**| **1,172.9 req/s** | 220.3 req/s | **⚡ 5.32x Faster** | **85.26 ms** | 453.85 ms (p99: 17.6s) |
| **Real GET (Sync)** | **4,066.8 req/s** | 1,679.0 req/s | **⚡ 2.42x Faster** | **24.59 ms** | 59.56 ms |
| **Real POST (Sync Pydantic)** | **1,845.0 req/s** | 935.3 req/s | **⚡ 1.97x Faster** | **54.20 ms** | 106.92 ms |
| **Real GET (Async I/O)** | **2,444.8 req/s** | 1,557.6 req/s | **⚡ 1.57x Faster** | **40.90 ms** | 64.20 ms |

### Profile B: Standard Load (c=50, 2,000 requests)

| Benchmark Workload | PyDataUI (`pyrustapi`) | FastAPI (`uvicorn + uvloop`) | Speedup Advantage | PyDataUI Latency (Mean) | FastAPI Latency (Mean) |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Real GET (Sync)** | **4,028.9 req/s** | 1,705.1 req/s | **⚡ 2.36x Faster** | **12.41 ms** | 29.32 ms |
| **Real POST (Sync Pydantic)** | **3,736.5 req/s** | 1,302.3 req/s | **⚡ 2.87x Faster** | **13.38 ms** | 38.39 ms |
| **Real POST (Async Pydantic)**| **2,311.5 req/s** | 1,388.6 req/s | **⚡ 1.66x Faster** | **21.63 ms** | 36.01 ms |
| **Real GET (Async I/O)** | **2,772.4 req/s** | 1,966.6 req/s | **⚡ 1.41x Faster** | **18.04 ms** | 25.42 ms |

> **Key Takeaway**: Under high concurrency, PyDataUI is **up to 5.3x faster** than FastAPI. FastAPI's event-loop queue suffers tail latency blowouts up to 17.6 seconds on async POST, while PyDataUI maintains p99 tail latency under 125 ms thanks to Tokio's multi-threaded work-stealing scheduler.

---

## 🔬 Benchmark Methodology & Environment

- **Hardware**: macOS Darwin (MacBook)
- **Python Version**: Python 3.13 / 3.11
- **Benchmarking Tool**: ApacheBench (`ab`) 2.3
- **FastAPI Server**: `uvicorn` with `uvloop` enabled, logging disabled (`log_level="error"`).
- **PyDataUI Server**: `pyrustapi` Rust/Tokio engine.
- **Fairness Controls**:
  - Identical Pydantic request models (`BookInput` with 5 fields including lists and floats).
  - Identical response models (`BookOutput`).
  - Warmup cycle of 200 requests executed before measurement rounds.
  - Concurrency level: **50 concurrent connections**, **2,000 total requests** per test.
  - Error rate across all tests: **0.00%** (zero failed requests).

---

## 📈 Detailed Test Results (c=50, n=2000)

### 1. Real POST (Sync Pydantic Parsing & Validation)
Tests HTTP request body reading, JSON parsing, Pydantic model validation, and serialized response generation.

```
Endpoint: POST /sync-post
Payload: {"title": "Designing Data-Intensive Applications", "author": "Martin Kleppmann", "pages": 616, "rating": 4.9, "tags": ["distributed-systems", "database"]}
Response: {"id": "book-pydataui-101", "title": "...", "author": "...", "reading_time_hours": 12.32, "status": "registered"}
```

| Metric | PyDataUI (`pyrustapi`) | FastAPI (`uvicorn + uvloop`) | Comparison |
| :--- | :---: | :---: | :---: |
| **Requests / Second** | **3,736.5 req/s** | 1,302.3 req/s | **⚡ 2.87x higher throughput** |
| **Mean Latency** | **13.38 ms** | 38.39 ms | **65.1% lower latency** |
| **Latency (across concurrent)** | **0.268 ms** | 0.768 ms | **2.87x faster** |
| **50th Percentile (p50)** | **13.0 ms** | 36.0 ms | **2.77x faster** |
| **90th Percentile (p90)** | **18.0 ms** | 38.0 ms | **2.11x faster** |
| **95th Percentile (p95)** | **20.0 ms** | 40.0 ms | **2.00x faster** |
| **99th Percentile (p99)** | **31.0 ms** | 118.0 ms | **3.81x faster tail latency** |
| **Transfer Rate** | **981.6 KB/s** | 375.2 KB/s | **2.62x transfer speed** |
| **Failed Requests** | **0 (0.00%)** | 0 (0.00%) | 100% Reliability |

---

### 2. Real GET (Sync JSON Response)
Tests raw HTTP routing, context dispatch, and JSON response delivery.

```
Endpoint: GET /sync-get
Response: {"message": "Hello from PyDataUI", "framework": "pydataui", "status": "success", "timestamp": 1728640000}
```

| Metric | PyDataUI (`pyrustapi`) | FastAPI (`uvicorn + uvloop`) | Comparison |
| :--- | :---: | :---: | :---: |
| **Requests / Second** | **4,028.9 req/s** | 1,705.1 req/s | **⚡ 2.36x higher throughput** |
| **Mean Latency** | **12.41 ms** | 29.32 ms | **57.7% lower latency** |
| **Latency (across concurrent)** | **0.248 ms** | 0.586 ms | **2.36x faster** |
| **50th Percentile (p50)** | **12.0 ms** | 29.0 ms | **2.42x faster** |
| **90th Percentile (p90)** | **18.0 ms** | 30.0 ms | **1.67x faster** |
| **95th Percentile (p95)** | **19.0 ms** | 31.0 ms | **1.63x faster** |
| **99th Percentile (p99)** | **22.0 ms** | 32.0 ms | **1.45x faster** |
| **Transfer Rate** | **842.0 KB/s** | 399.6 KB/s | **2.11x transfer speed** |
| **Failed Requests** | **0 (0.00%)** | 0 (0.00%) | 100% Reliability |

---

### 3. Real POST (Async Pydantic Handling)
Tests asynchronous request handling combined with Pydantic validation and non-blocking scheduling.

| Metric | PyDataUI (`pyrustapi`) | FastAPI (`uvicorn + uvloop`) | Comparison |
| :--- | :---: | :---: | :---: |
| **Requests / Second** | **2,311.5 req/s** | 1,388.6 req/s | **⚡ 1.66x higher throughput** |
| **Mean Latency** | **21.63 ms** | 36.01 ms | **39.9% lower latency** |
| **50th Percentile (p50)** | **20.0 ms** | 35.0 ms | **1.75x faster** |
| **90th Percentile (p90)** | **28.0 ms** | 37.0 ms | **1.32x faster** |
| **95th Percentile (p95)** | **30.0 ms** | 37.0 ms | **1.23x faster** |
| **Transfer Rate** | **607.2 KB/s** | 400.0 KB/s | **1.52x transfer speed** |
| **Failed Requests** | **0 (0.00%)** | 0 (0.00%) | 100% Reliability |

---

### 4. Real GET (Async I/O Simulation)
Simulates real-world database or API latency using non-blocking asynchronous event loop dispatch (`await asyncio.sleep(0.001)`).

| Metric | PyDataUI (`pyrustapi`) | FastAPI (`uvicorn + uvloop`) | Comparison |
| :--- | :---: | :---: | :---: |
| **Requests / Second** | **2,772.4 req/s** | 1,966.6 req/s | **⚡ 1.41x higher throughput** |
| **Mean Latency** | **18.04 ms** | 25.42 ms | **29.0% lower latency** |
| **50th Percentile (p50)** | **17.0 ms** | 25.0 ms | **1.47x faster** |
| **90th Percentile (p90)** | **22.0 ms** | 27.0 ms | **1.23x faster** |
| **95th Percentile (p95)** | **25.0 ms** | 28.0 ms | **1.12x faster** |
| **Transfer Rate** | **595.6 KB/s** | 474.4 KB/s | **1.26x transfer speed** |
| **Failed Requests** | **0 (0.00%)** | 0 (0.00%) | 100% Reliability |

---

## 🏗️ Why is PyDataUI Faster?

1. **Compiled Rust Core Engine (`pyrustapi`)**:
   - HTTP parsing, TCP socket management, keep-alive framing, and header processing are handled in compiled Rust using Tokio and Hyper.
   - Python only executes the application logic and handler body, eliminating Python interpreter overhead for low-level HTTP protocol handling.

2. **Optimized Multi-Threaded Dispatching**:
   - Tokio distributes incoming requests across native OS threads before bridging into Python, maximizing CPU core utilization.

3. **Zero-Overhead Memory Shuttling**:
   - Request payloads and headers are mapped directly from Rust memory into Python objects via PyO3 without redundant intermediate string copying.

---

## 📱 Mobile & Cold-Start Optimization Benchmarks (v1.1.0)

With the release of PyDataUI v1.1.0, comprehensive framework-level and transport-layer optimizations were benchmarked for mobile and local execution:

| Metric / Workload | Before Optimization | After v1.1.0 Optimization | Speedup / Improvement |
| :--- | :--- | :--- | :--- |
| **Top-Level Cold Start (`import pydataui`)** | `562.89 ms` | **`10.68 ms`** | **⚡ 52.7x Faster (−98.1%)** |
| **Est. Mobile / Chaquopy Import Time** | `~2,800–3,500 ms` | **`< 1,200 ms`** | **⚡ 60% Faster Startup** |
| **Request Transport Latency (Loopback)** | `~12–25 ms` (TCP Socket) | **`< 1.0 ms` (In-Process JNI)** | **⚡ 92% Transport Latency Reduction** |
| **Action Payload (Button / Event)** | Full `#pdu-root` (~15–80 KB) | **0 B (Minimal Scoped)** | **⚡ 100% Redundant DOM State Eliminated** |
| **Input Change Serialization** | Full `#pdu-root` | **`hx-include="this"` (~12 B)** | **⚡ 99.8% Payload Reduction** |
| **Response Transfer Size (Mobile Mode)**| Raw HTML Fragment | **GZip Compressed (>500B)** | **⚡ 70–85% Transfer Size Shrinkage** |
| **Subtree Partial SSR Re-render** | Full Page DOM Swap | **Targeted Component Only** | **⚡ <15–30 ms DOM Mutation** |

---

## 🔁 How to Reproduce

You can reproduce these benchmarks on your local machine using the benchmark harness included in the repository:

```bash
# Ensure dependencies are installed
pip install -e .
pip install fastapi uvicorn uvloop

# Run the benchmark suite (2000 requests, 50 concurrency)
python benchmarks/run_benchmark.py --requests 2000 --concurrency 50
```

To run with custom parameters:
```bash
python benchmarks/run_benchmark.py --requests 5000 --concurrency 100
```
