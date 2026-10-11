#!/usr/bin/env python3
"""
Comprehensive Benchmark Runner: PyDataUI (PyRustAPI) vs FastAPI (Uvicorn).
Measures Real GET and Real POST throughput, latency, and percentiles.
"""
import argparse
import json
import os
from pathlib import Path
import re
import socket
import subprocess
import sys
import tempfile
import time
from urllib.request import Request, build_opener, ProxyHandler


def get_free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('127.0.0.1', 0))
        return s.getsockname()[1]


def wait_until_ready(port: int, path: str = "/sync-get", timeout: float = 10.0) -> bool:
    opener = build_opener(ProxyHandler({}))
    start = time.time()
    url = f"http://127.0.0.1:{port}{path}"
    while time.time() - start < timeout:
        try:
            req = Request(url)
            with opener.open(req, timeout=1.0) as resp:
                if resp.status == 200:
                    return True
        except Exception:
            time.sleep(0.1)
    return False


def run_ab(
    url: str,
    requests: int,
    concurrency: int,
    post_file: str = None,
) -> dict:
    cmd = ["ab", "-n", str(requests), "-c", str(concurrency)]
    if post_file:
        cmd.extend(["-p", post_file, "-T", "application/json"])
    cmd.append(url)

    res = subprocess.run(cmd, capture_output=True, text=True)
    out = res.stdout

    rps_match = re.search(r"Requests per second:\s+([0-9.]+)", out)
    mean_lat_match = re.search(r"Time per request:\s+([0-9.]+)\s+\[ms\]\s+\(mean\)", out)
    concurrent_lat_match = re.search(
        r"Time per request:\s+([0-9.]+)\s+\[ms\]\s+\(mean, across all concurrent requests\)", out
    )
    failed_match = re.search(r"Failed requests:\s+([0-9]+)", out)
    transfer_match = re.search(r"Transfer rate:\s+([0-9.]+)\s+\[Kbytes/sec\]", out)

    p50_match = re.search(r"50%\s+([0-9]+)", out)
    p90_match = re.search(r"90%\s+([0-9]+)", out)
    p95_match = re.search(r"95%\s+([0-9]+)", out)
    p99_match = re.search(r"99%\s+([0-9]+)", out)

    return {
        "requests_per_sec": float(rps_match.group(1)) if rps_match else 0.0,
        "mean_latency_ms": float(mean_lat_match.group(1)) if mean_lat_match else 0.0,
        "concurrent_latency_ms": float(concurrent_lat_match.group(1)) if concurrent_lat_match else 0.0,
        "failed_requests": int(failed_match.group(1)) if failed_match else 0,
        "transfer_rate_kb_s": float(transfer_match.group(1)) if transfer_match else 0.0,
        "p50_ms": float(p50_match.group(1)) if p50_match else 0.0,
        "p90_ms": float(p90_match.group(1)) if p90_match else 0.0,
        "p95_ms": float(p95_match.group(1)) if p95_match else 0.0,
        "p99_ms": float(p99_match.group(1)) if p99_match else 0.0,
    }


def main():
    parser = argparse.ArgumentParser(description="PyDataUI vs FastAPI Benchmark Harness")
    parser.add_argument("--requests", type=int, default=2000, help="Number of requests per test (default: 2000)")
    parser.add_argument("--concurrency", type=int, default=50, help="Concurrency level (default: 50)")
    parser.add_argument("--warmup", type=int, default=200, help="Warmup requests (default: 200)")
    parser.add_argument("--output", type=str, default="benchmarks/benchmark_results.json", help="Path to save JSON results")
    args = parser.parse_args()

    repo_dir = Path(__file__).resolve().parent.parent
    bench_dir = Path(__file__).resolve().parent

    print("=" * 80)
    print("🔥 PYDATAUI (PyRustAPI) vs FASTAPI (Uvicorn + uvloop) REAL BENCHMARK")
    print(f"Total Requests: {args.requests} | Concurrency: {args.concurrency} | Warmup: {args.warmup}")
    print("=" * 80)

    # Prepare POST test payload
    payload = {
        "title": "Designing Data-Intensive Applications",
        "author": "Martin Kleppmann",
        "pages": 616,
        "rating": 4.9,
        "tags": ["distributed-systems", "database", "engineering"],
    }
    with tempfile.NamedTemporaryFile("w", delete=False, suffix=".json") as f:
        json.dump(payload, f)
        post_file = f.name

    test_cases = [
        ("Real GET (Sync)", "/sync-get", False),
        ("Real GET (Async I/O)", "/async-get", False),
        ("Real POST (Sync Pydantic)", "/sync-post", True),
        ("Real POST (Async Pydantic)", "/async-post", True),
    ]

    env = dict(os.environ, PYTHONPATH=str(repo_dir))
    results = {}

    for name, path, is_post in test_cases:
        print(f"\n▶ Benchmarking: {name}")

        # 1. Run PyDataUI
        pdu_port = get_free_port()
        pdu_proc = subprocess.Popen(
            [sys.executable, str(bench_dir / "pydataui_app.py"), "--port", str(pdu_port)],
            env=env,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        if not wait_until_ready(pdu_port, "/sync-get"):
            pdu_proc.kill()
            raise RuntimeError(f"PyDataUI failed to start on port {pdu_port}")

        # Warmup PyDataUI
        run_ab(
            f"http://127.0.0.1:{pdu_port}{path}",
            args.warmup,
            min(10, args.concurrency),
            post_file if is_post else None,
        )
        # Measured run PyDataUI
        pdu_res = run_ab(
            f"http://127.0.0.1:{pdu_port}{path}",
            args.requests,
            args.concurrency,
            post_file if is_post else None,
        )
        pdu_proc.terminate()
        pdu_proc.wait()

        # 2. Run FastAPI
        fa_port = get_free_port()
        fa_proc = subprocess.Popen(
            [sys.executable, str(bench_dir / "fastapi_app.py"), "--port", str(fa_port)],
            env=env,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        if not wait_until_ready(fa_port, "/sync-get"):
            fa_proc.kill()
            raise RuntimeError(f"FastAPI failed to start on port {fa_port}")

        # Warmup FastAPI
        run_ab(
            f"http://127.0.0.1:{fa_port}{path}",
            args.warmup,
            min(10, args.concurrency),
            post_file if is_post else None,
        )
        # Measured run FastAPI
        fa_res = run_ab(
            f"http://127.0.0.1:{fa_port}{path}",
            args.requests,
            args.concurrency,
            post_file if is_post else None,
        )
        fa_proc.terminate()
        fa_proc.wait()

        speedup = pdu_res["requests_per_sec"] / fa_res["requests_per_sec"] if fa_res["requests_per_sec"] > 0 else 1.0

        results[name] = {
            "endpoint": path,
            "method": "POST" if is_post else "GET",
            "pydataui": pdu_res,
            "fastapi": fa_res,
            "speedup": round(speedup, 2),
        }

        print(f"  PyDataUI: {pdu_res['requests_per_sec']:,.1f} req/s | Mean Latency: {pdu_res['mean_latency_ms']:.2f} ms | p95: {pdu_res['p95_ms']} ms")
        print(f"  FastAPI:  {fa_res['requests_per_sec']:,.1f} req/s | Mean Latency: {fa_res['mean_latency_ms']:.2f} ms | p95: {fa_res['p95_ms']} ms")
        print(f"  ⚡ Speedup: PyDataUI is {speedup:.2f}x faster")

    # Cleanup temp file
    try:
        os.remove(post_file)
    except OSError:
        pass

    # Save to JSON
    out_path = repo_dir / args.output
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w") as f:
        json.dump(
            {
                "metadata": {
                    "requests": args.requests,
                    "concurrency": args.concurrency,
                    "platform": sys.platform,
                    "python_version": sys.version.split()[0],
                    "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                },
                "results": results,
            },
            f,
            indent=2,
        )
    print(f"\nSaved detailed benchmark JSON to: {out_path}")

    # Generate Markdown Summary
    print("\n" + "=" * 90)
    print("🏆 FINAL BENCHMARK SUMMARY (Real Measured Results)")
    print("=" * 90)
    header = f"{'Benchmark Test':<30} | {'PyDataUI (RPS)':<16} | {'FastAPI (RPS)':<15} | {'Speedup':<10} | {'PDU Latency':<12} | {'FA Latency':<12}"
    print(header)
    print("-" * 105)
    for name, data in results.items():
        pdu_rps = f"{data['pydataui']['requests_per_sec']:,.1f}"
        fa_rps = f"{data['fastapi']['requests_per_sec']:,.1f}"
        spd = f"{data['speedup']:.2f}x"
        pdu_lat = f"{data['pydataui']['mean_latency_ms']:.2f} ms"
        fa_lat = f"{data['fastapi']['mean_latency_ms']:.2f} ms"
        print(f"{name:<30} | {pdu_rps:<16} | {fa_rps:<15} | {spd:<10} | {pdu_lat:<12} | {fa_lat:<12}")
    print("=" * 105)


if __name__ == "__main__":
    main()
