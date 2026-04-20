"""
Load test script cho TA_Chatbot backend — Day 13 Lab.
Gửi nhiều request đồng thời để đo latency P50/P95/P99.
Chạy: python scripts/load_test.py --concurrency 5
"""
import argparse
import concurrent.futures
import json
import time
from pathlib import Path

import httpx

# URL của TA_Chatbot backend
BASE_URL = "http://127.0.0.1:8000"
# File chứa các câu hỏi mẫu (format: {"content": "...", "user_id": "..."})
QUERIES = Path("data/sample_queries.jsonl")


def send_request(client: httpx.Client, payload: dict) -> dict:
    """Gửi một request POST /chat và trả về kết quả."""
    try:
        t_start = time.perf_counter()
        r = client.post(f"{BASE_URL}/chat", json=payload, timeout=60.0)
        latency_ms = (time.perf_counter() - t_start) * 1000

        # Lấy correlation_id từ response header
        correlation_id = r.headers.get("x-request-id", "N/A")
        resp_time = r.headers.get("x-response-time-ms", "N/A")

        status_icon = "✅" if r.status_code == 200 else "❌"
        print(
            f"{status_icon} [{r.status_code}] "
            f"user={payload.get('user_id', 'anon')} | "
            f"req_id={correlation_id} | "
            f"server={resp_time}ms | client={latency_ms:.0f}ms"
        )
        return {"status": r.status_code, "latency_ms": latency_ms, "correlation_id": correlation_id}
    except httpx.ConnectError:
        print(f"❌ Không kết nối được {BASE_URL} — hãy chắc backend đang chạy!")
        return {"status": 0, "latency_ms": 0, "correlation_id": "N/A"}
    except Exception as e:
        print(f"❌ Lỗi: {e}")
        return {"status": 0, "latency_ms": 0, "correlation_id": "N/A"}


def main() -> None:
    parser = argparse.ArgumentParser(description="Load test cho TA_Chatbot — Day 13 Lab")
    parser.add_argument("--concurrency", type=int, default=1, help="Số request đồng thời (mặc định: 1)")
    args = parser.parse_args()

    if not QUERIES.exists():
        print(f"❌ Không tìm thấy {QUERIES}. Hãy chạy từ thư mục gốc Lab13-Observability/")
        return

    lines = [ln for ln in QUERIES.read_text(encoding="utf-8").splitlines() if ln.strip()]
    print(f"\n🚀 Bắt đầu load test: {len(lines)} requests | concurrency={args.concurrency} | target={BASE_URL}")
    print("-" * 70)

    results = []
    t_total_start = time.perf_counter()

    with httpx.Client(timeout=60.0) as client:
        if args.concurrency > 1:
            with concurrent.futures.ThreadPoolExecutor(max_workers=args.concurrency) as executor:
                futures = [
                    executor.submit(send_request, client, json.loads(ln))
                    for ln in lines
                ]
                for f in concurrent.futures.as_completed(futures):
                    results.append(f.result())
        else:
            for ln in lines:
                results.append(send_request(client, json.loads(ln)))

    total_time = (time.perf_counter() - t_total_start) * 1000
    latencies = [r["latency_ms"] for r in results if r["latency_ms"] > 0]
    success_count = sum(1 for r in results if r["status"] == 200)

    print("-" * 70)
    print(f"\n📊 KẾT QUẢ LOAD TEST")
    print(f"   Tổng requests : {len(results)}")
    print(f"   Thành công    : {success_count}/{len(results)}")
    print(f"   Thời gian tổng: {total_time:.0f}ms")
    if latencies:
        sorted_lat = sorted(latencies)
        p50 = sorted_lat[len(sorted_lat) // 2]
        p95_idx = int(len(sorted_lat) * 0.95)
        p99_idx = int(len(sorted_lat) * 0.99)
        print(f"   Latency P50   : {p50:.0f}ms")
        print(f"   Latency P95   : {sorted_lat[min(p95_idx, len(sorted_lat)-1)]:.0f}ms")
        print(f"   Latency P99   : {sorted_lat[min(p99_idx, len(sorted_lat)-1)]:.0f}ms")

    print(f"\n💡 Xem metrics chi tiết: curl {BASE_URL}/obs-metrics")


if __name__ == "__main__":
    main()
