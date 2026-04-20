"""
FastAPI Backend for TA Chatbot
Handles AI agent logic, RAG, escalation, and security.
Day 13 Observability Lab — Đã tích hợp structlog, correlation ID, PII scrubbing, metrics.
"""

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Optional
import os
import time
from dotenv import load_dotenv
import sys
from pathlib import Path

# Thêm thư mục gốc backend vào sys.path để import module ngang cấp
sys.path.insert(0, str(Path(__file__).parent.parent))

from agent import stream_chat
from utils.storage import get_metrics, update_metric
from utils.email_service import send_escalation_email

from app.config import MAX_REQUESTS_PER_WINDOW, RATE_LIMIT_WINDOW_SECONDS, PER_USER_DAILY_BUDGET, GLOBAL_DAILY_BUDGET
from app.rate_limiter import RateLimiter
from app.cost_guard import CostGuard
from app.health import HealthMonitor

# === OBSERVABILITY — Day 13 Lab ===
from obs.logging_config import configure_logging, get_logger
from obs.middleware import CorrelationIdMiddleware
from obs.pii import hash_user_id, summarize_text
from obs.metrics import record_request, record_error, snapshot
from obs.tracing import tracing_enabled
from structlog.contextvars import bind_contextvars

# Khởi động structured logging trước khi làm bất cứ thứ gì
load_dotenv()
configure_logging()
log = get_logger()

app = FastAPI(
    title="TA Chatbot API",
    description="AI Teaching Assistant for C/C++ — Day 13 Observability Lab",
    version="2.0.0"
)

# Middleware: CorrelationId phải đăng ký TRƯỚC CORS
app.add_middleware(CorrelationIdMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Khởi tạo các module bảo mật hiện có
rate_limiter = RateLimiter(max_requests=MAX_REQUESTS_PER_WINDOW, window_seconds=RATE_LIMIT_WINDOW_SECONDS)
cost_guard = CostGuard(per_user_budget=PER_USER_DAILY_BUDGET, global_budget=GLOBAL_DAILY_BUDGET)
health_monitor = HealthMonitor()


# ===== Models =====
class ChatMessage(BaseModel):
    content: str
    user_id: Optional[str] = None

class ChatResponse(BaseModel):
    content: str
    cost: float
    remaining_budget: float
    correlation_id: Optional[str] = None
    warning: Optional[str] = None

class MetricsResponse(BaseModel):
    helpful: int
    unhelpful: int
    escalated: int
    total: int

class HealthResponse(BaseModel):
    status: str
    uptime_seconds: float
    total_requests: int
    error_count: int
    error_rate: float


# ===== Startup =====
@app.on_event("startup")
async def startup() -> None:
    log.info(
        "ta_chatbot_started",
        service="api",
        payload={
            "app_env": os.getenv("APP_ENV", "dev"),
            "tracing_enabled": tracing_enabled(),
        },
    )


# ===== Routes =====
@app.get("/")
async def root():
    """Thông tin API"""
    return {
        "name": "TA Chatbot API",
        "version": "2.0.0",
        "description": "AI Teaching Assistant Backend — Day 13 Lab",
        "docs": "/docs",
        "health": "/health",
        "obs_metrics": "/obs-metrics",
    }


@app.get("/health")
async def health(request: Request):
    """Kiểm tra trạng thái hệ thống + tracing status"""
    stats = health_monitor.get_stats()
    return {
        **stats,
        "tracing_enabled": tracing_enabled(),
        "correlation_id": getattr(request.state, "correlation_id", "N/A"),
    }


@app.get("/obs-metrics")
async def obs_metrics():
    """Observability metrics: latency P50/P95/P99, cost, tokens, quality — dùng cho dashboard"""
    return snapshot()


@app.post("/chat", response_model=ChatResponse)
async def chat(request: Request, message: ChatMessage):
    """Xử lý tin nhắn từ học viên qua AI agent"""
    user_id = message.user_id or "anonymous"
    correlation_id = getattr(request.state, "correlation_id", "N/A")

    # Làm giàu structlog context — user_id_hash, session_id, feature, model tự động vào log
    bind_contextvars(
        user_id_hash=hash_user_id(user_id),
        session_id=user_id,
        feature="chat",
        model=os.getenv("LLM_MODEL", "gpt-4o"),
        env=os.getenv("APP_ENV", "dev"),
    )

    log.info(
        "request_received",
        service="api",
        payload={"message_preview": summarize_text(message.content)},
    )

    t_start = time.perf_counter()

    try:
        # Kiểm tra rate limit
        if not rate_limiter.check(user_id):
            remaining = rate_limiter.get_remaining(user_id)
            health_monitor.record_request(success=False)
            record_error("RateLimitExceeded")
            raise HTTPException(
                status_code=429,
                detail=f"Rate limit exceeded: {remaining}/{MAX_REQUESTS_PER_WINDOW} remaining"
            )

        # Kiểm tra budget người dùng
        allowed, msg = cost_guard.check_user_budget(user_id)
        if not allowed:
            health_monitor.record_request(success=False)
            record_error("BudgetExceeded")
            raise HTTPException(status_code=402, detail=msg)

        # Kiểm tra global budget
        allowed, msg = cost_guard.check_global_budget()
        if not allowed:
            health_monitor.record_request(success=False)
            record_error("GlobalBudgetExceeded")
            raise HTTPException(status_code=402, detail=f"Global: {msg}")

        # Gọi agent và lấy response
        response_chunks = []
        for chunk in stream_chat(message.content, []):
            response_chunks.append(chunk)

        full_response = "".join(response_chunks)
        latency_ms = int((time.perf_counter() - t_start) * 1000)

        # Ước tính token và chi phí
        input_tokens = len(message.content) // 4
        output_tokens = len(full_response) // 4
        cost_guard.record_usage(user_id, input_tokens, output_tokens)
        cost_per_req = (input_tokens / 1_000_000) * 5 + (output_tokens / 1_000_000) * 15

        # Ghi metrics observability
        record_request(
            latency_ms=latency_ms,
            cost_usd=cost_per_req,
            tokens_in=input_tokens,
            tokens_out=output_tokens,
        )
        update_metric("total", 1)

        user_stats = cost_guard.get_user_stats(user_id)
        warning = None
        if user_stats['usage_percent'] > 80:
            warning = f"⚠️ Budget warning: {user_stats['usage_percent']:.1f}% used"

        health_monitor.record_request(success=True)

        log.info(
            "response_sent",
            service="api",
            latency_ms=latency_ms,
            tokens_in=input_tokens,
            tokens_out=output_tokens,
            payload={"answer_preview": summarize_text(full_response)},
        )

        return ChatResponse(
            content=full_response,
            cost=user_stats['spent_today'],
            remaining_budget=user_stats['remaining'],
            correlation_id=correlation_id,
            warning=warning,
        )

    except HTTPException:
        raise
    except Exception as e:
        latency_ms = int((time.perf_counter() - t_start) * 1000)
        error_type = type(e).__name__
        record_error(error_type)
        health_monitor.record_request(success=False)
        log.error(
            "request_failed",
            service="api",
            error_type=error_type,
            latency_ms=latency_ms,
            payload={"detail": str(e), "message_preview": summarize_text(message.content)},
        )
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/escalate")
async def escalate(data: Dict):
    """Chuyển câu hỏi cho TA người thật qua email"""
    try:
        success = send_escalation_email(data)
        if success:
            update_metric("escalated", 1)
            health_monitor.record_request(success=True)
            log.info("escalation_sent", service="api", payload={"status": "success"})
            return {"status": "success", "message": "Escalation email sent"}
        else:
            health_monitor.record_request(success=False)
            raise HTTPException(status_code=500, detail="Failed to send email")
    except HTTPException:
        raise
    except Exception as e:
        health_monitor.record_request(success=False)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/metrics", response_model=MetricsResponse)
async def metrics():
    """Metrics học viên từ storage: helpful/unhelpful/escalated/total"""
    try:
        metrics_data = get_metrics()
        health_monitor.record_request(success=True)
        return MetricsResponse(**metrics_data)
    except Exception as e:
        log.error("metrics_error", service="api", payload={"detail": str(e)})
        health_monitor.record_request(success=False)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/feedback")
async def feedback(data: Dict):
    """Ghi nhận phản hồi học viên: helpful/unhelpful"""
    try:
        feedback_type = data.get("type")
        if feedback_type in ["helpful", "unhelpful", "escalated"]:
            update_metric(feedback_type, 1)
            health_monitor.record_request(success=True)
            log.info("feedback_recorded", service="api", payload={"type": feedback_type})
            return {"status": "success", "message": f"Feedback recorded: {feedback_type}"}
        else:
            raise ValueError(f"Invalid feedback type: {feedback_type}")
    except Exception as e:
        health_monitor.record_request(success=False)
        raise HTTPException(status_code=400, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
