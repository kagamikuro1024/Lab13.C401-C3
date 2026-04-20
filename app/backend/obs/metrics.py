"""
Module thu thập metrics in-memory cho TA_Chatbot.
Cung cấp dữ liệu cho 6 panels của dashboard và endpoint GET /obs-metrics.
"""
from __future__ import annotations

from collections import Counter
from statistics import mean

# --- Bộ nhớ tạm lưu trữ metrics (in-process, reset khi restart) ---
REQUEST_LATENCIES: list[int] = []      # Danh sách latency mỗi request (ms)
REQUEST_COSTS: list[float] = []        # Danh sách chi phí mỗi request (USD)
REQUEST_TOKENS_IN: list[int] = []      # Số token đầu vào mỗi request
REQUEST_TOKENS_OUT: list[int] = []     # Số token đầu ra mỗi request
QUALITY_SCORES: list[float] = []       # Điểm chất lượng (hiện tại dùng 0.8 cố định)
ERRORS: Counter[str] = Counter()       # Đếm lỗi theo loại
TRAFFIC: int = 0                       # Tổng số request đã nhận


def record_request(
    latency_ms: int,
    cost_usd: float = 0.0,
    tokens_in: int = 0,
    tokens_out: int = 0,
    quality_score: float = 0.8,
) -> None:
    """Ghi nhận một request thành công vào bộ nhớ metrics."""
    global TRAFFIC
    TRAFFIC += 1
    REQUEST_LATENCIES.append(latency_ms)
    REQUEST_COSTS.append(cost_usd)
    REQUEST_TOKENS_IN.append(tokens_in)
    REQUEST_TOKENS_OUT.append(tokens_out)
    QUALITY_SCORES.append(quality_score)


def record_error(error_type: str) -> None:
    """Ghi nhận một lỗi runtime theo tên loại lỗi."""
    ERRORS[error_type] += 1


def percentile(values: list[int], p: int) -> float:
    """Tính phân vị thứ p của danh sách giá trị."""
    if not values:
        return 0.0
    items = sorted(values)
    idx = max(0, min(len(items) - 1, round((p / 100) * len(items) + 0.5) - 1))
    return float(items[idx])


def snapshot() -> dict:
    """Trả về bản snapshot các metrics hiện tại — dùng cho endpoint GET /obs-metrics."""
    return {
        "traffic": TRAFFIC,
        "latency_p50": percentile(REQUEST_LATENCIES, 50),
        "latency_p95": percentile(REQUEST_LATENCIES, 95),
        "latency_p99": percentile(REQUEST_LATENCIES, 99),
        "avg_cost_usd": round(mean(REQUEST_COSTS), 6) if REQUEST_COSTS else 0.0,
        "total_cost_usd": round(sum(REQUEST_COSTS), 6),
        "tokens_in_total": sum(REQUEST_TOKENS_IN),
        "tokens_out_total": sum(REQUEST_TOKENS_OUT),
        "error_breakdown": dict(ERRORS),
        "quality_avg": round(mean(QUALITY_SCORES), 4) if QUALITY_SCORES else 0.0,
    }
