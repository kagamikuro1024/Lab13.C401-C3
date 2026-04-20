"""
Middleware gắn Correlation ID vào mỗi HTTP request của TA_Chatbot.
Đảm bảo mọi log trong một request có cùng correlation_id để truy vết.
Tác giả: Trung (Tech Lead)
"""
from __future__ import annotations

import time
import uuid

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from structlog.contextvars import bind_contextvars, clear_contextvars


class CorrelationIdMiddleware(BaseHTTPMiddleware):
    """
    Middleware tự động gắn x-request-id vào mỗi request.

    Luồng xử lý:
    1. Xóa contextvars cũ (tránh rò rỉ giữa các request)
    2. Lấy x-request-id từ header hoặc tự sinh mới
    3. Gắn vào structlog context → xuất hiện trong MỌI log của request này
    4. Ghi correlation_id và response time vào response headers
    """

    async def dispatch(self, request: Request, call_next):
        # Xóa context của request trước — quan trọng khi dùng thread pool
        clear_contextvars()

        # Lấy x-request-id từ header hoặc sinh UUID mới dạng req-<8-hex>
        raw = request.headers.get("x-request-id", "")
        correlation_id = raw if raw else f"req-{uuid.uuid4().hex[:8]}"

        # Gắn vào structlog context — tất cả log trong request này tự có correlation_id
        bind_contextvars(correlation_id=correlation_id)

        # Lưu vào request.state để endpoint có thể truy cập
        request.state.correlation_id = correlation_id

        # Đo thời gian xử lý request
        t_start = time.perf_counter()
        response = await call_next(request)
        elapsed_ms = int((time.perf_counter() - t_start) * 1000)

        # Trả thông tin ngược về client qua response headers
        response.headers["x-request-id"] = correlation_id
        response.headers["x-response-time-ms"] = str(elapsed_ms)

        return response
