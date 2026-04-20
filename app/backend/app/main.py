"""
FastAPI Backend for TA Chatbot
Handles AI agent logic, RAG, escalation, and security.
Day 13 Observability Lab — Đã tích hợp structlog, correlation ID, PII scrubbing, metrics.
"""

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Optional
import os
import time
# === Load Environment Variables FIRST ===
import os
from pathlib import Path
from dotenv import load_dotenv

# Trỏ thẳng vào file .env trong thư mục app/backend
env_path = Path(__file__).parent.parent / ".env"
# Ép buộc ghi đè nếu đã lỡ load file .env khác trước đó
load_dotenv(dotenv_path=env_path, override=True)

import sys
from pathlib import Path

# Thêm thư mục gốc backend vào sys.path để import module ngang cấp
sys.path.insert(0, str(Path(__file__).parent.parent))

from agent import chat as agent_chat
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
from structlog.contextvars import bind_contextvars
import json

# Khởi động structured logging
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


@app.on_event("startup")
async def startup() -> None:
    log.info(
        "ta_chatbot_started",
        service="api",
        payload={
            "app_env": os.getenv("APP_ENV", "dev"),
            "observability": "local_dashboard_enabled",
        },
    )


# ===== Routes =====
@app.get("/")
async def root():
    """Thông tin API"""
    return {
        "name": "TA Chatbot API",
        "version": "2.1.0",
        "description": "AI Teaching Assistant Backend — Local Observability Edition",
        "docs": "/docs",
        "health": "/health",
        "dashboard": "/obs-dashboard",
    }


@app.get("/health")
async def health(request: Request):
    """Kiểm tra trạng thái hệ thống"""
    stats = health_monitor.get_stats()
    return {
        **stats,
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
            log.warning("budget_exceeded", service="api", level="warning", user_id=user_id, payload={"detail": msg})
            raise HTTPException(status_code=402, detail=msg)

        # Kiểm tra global budget
        allowed, msg = cost_guard.check_global_budget()
        if not allowed:
            health_monitor.record_request(success=False)
            record_error("GlobalBudgetExceeded")
            log.error("global_budget_exceeded", service="api", level="error", payload={"detail": msg})
            raise HTTPException(status_code=402, detail=f"Global: {msg}")

        # Gọi agent (regular function — @observe hoạt động đúng với Langfuse v3)
        full_response = agent_chat(message.content, [])
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


# File lưu trữ ID đã đánh giá để đảm bảo bền vững khi reload server
FEEDBACK_IDS_FILE = Path(__file__).parent.parent.parent.parent / "data" / "feedback_ids.json"

def get_evaluated_ids():
    if not FEEDBACK_IDS_FILE.exists(): return set()
    try:
        with open(FEEDBACK_IDS_FILE, "r") as f:
            return set(json.load(f))
    except: return set()

def save_evaluated_id(target_id: str):
    ids = get_evaluated_ids()
    ids.add(target_id)
    with open(FEEDBACK_IDS_FILE, "w") as f:
        json.dump(list(ids), f)

@app.post("/feedback")
async def feedback(data: Dict):
    """Ghi nhận đánh giá của học viên kèm nội dung câu trả lời (Dành cho Admin giám sát)"""
    try:
        f_type = data.get("type", "helpful")
        target_id = data.get("target_id")
        answer_content = data.get("answer_content", "N/A")
        
        if not target_id:
            raise HTTPException(status_code=400, detail="Missing target_id")
            
        if target_id in get_evaluated_ids():
            return {"status": "ignored", "message": "Already evaluated"}
            
        save_evaluated_id(target_id)
        update_metric(f_type, 1)
        
        log.info(
            "feedback_recorded", 
            service="api", 
            level="info", 
            payload={
                "type": f_type, 
                "target_id": target_id,
                "answer_content": answer_content
            }
        )
        health_monitor.record_request(success=True)
        return {"status": "success"}
    except Exception as e:
        log.error("feedback_failed", service="api", error=str(e))
        raise HTTPException(status_code=500)


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


@app.get("/api/obs/stats")
async def get_obs_stats():
    """Aggregation logic for local dashboard - v2.3 Pro (6 Panels + Alerts)"""
    root_dir = Path(__file__).parent.parent.parent.parent
    log_file = root_dir / "data" / "logs.jsonl"
    
    if not log_file.exists():
        return {"error": f"Logs not found at {log_file}"}
    
    stats = {
        "total_requests": 0, "avg_latency": 0, "p90_latency": 0, "total_cost": 0,
        "tokens_in": 0, "tokens_out": 0, "error_count": 0, "escalated_count": 0,
        "transactions": [], "alerts": []
    }
    
    data_map = {}
    latencies = []

    try:
        with open(log_file, "rb") as f:
            f.seek(0, os.SEEK_END)
            size = f.tell()
            f.seek(max(0, size - 204800)) # Read last 200KB
            content = f.read().decode("utf-8", errors="ignore")
            lines = content.splitlines()

            for line in lines:
                try:
                    log_data = json.loads(line)
                    cid = log_data.get("correlation_id")
                    event = log_data.get("event")
                    if not cid or cid == "N/A":
                        if event == "escalation_sent": stats["escalated_count"] += 1
                        continue
                    
                    if cid not in data_map:
                        data_map[cid] = {"id": cid, "ts": log_data.get("ts"), "status": "pending"}
                    
                    payload = log_data.get("payload", {})
                    if event == "request_received":
                        data_map[cid]["input"] = payload.get("message_preview")
                    elif event == "response_sent":
                        stats["total_requests"] += 1
                        lat = log_data.get("latency_ms", 0)
                        latencies.append(lat)
                        tin, tout = log_data.get("tokens_in", 0), log_data.get("tokens_out", 0)
                        stats["tokens_in"] += tin
                        stats["tokens_out"] += tout
                        cost = (tin / 1000000) * 0.15 + (tout / 1000000) * 0.60
                        stats["total_cost"] += cost
                        data_map[cid].update({"status": "success", "output": payload.get("answer_preview"), "latency": lat, "tokens": tin+tout, "cost": cost})
                    elif event == "request_failed":
                        stats["error_count"] += 1
                        data_map[cid].update({"status": "failed"})
                    elif event == "escalation_sent":
                        stats["escalated_count"] += 1
                        data_map[cid]["escalated"] = True
                except: continue
                
        if latencies:
            latencies.sort()
            stats["avg_latency"] = sum(latencies) / len(latencies)
            stats["p90_latency"] = latencies[int(len(latencies) * 0.9)]
            
            # Chỉ lấy các transaction có nội dung (Input hoặc Output) để hiển thị ở bảng chính
            filtered_txs = [tx for tx in data_map.values() if tx.get("input") or tx.get("output")]
            stats["transactions"] = sorted(filtered_txs, key=lambda x: x.get("ts", ""), reverse=True)[:20]
            
        # Alert Logic
        if stats["p90_latency"] > 2000:
            stats["alerts"].append({"type": "HighLatency", "msg": "P90 Latency > 2s", "runbook": "#L30"})
        if stats["total_cost"] > 8.0:
            stats["alerts"].append({"type": "BudgetWarning", "msg": "Chi phí tiệm cận 80% hạn mức", "runbook": "#L40"})
        if stats["error_count"] > 0:
            stats["alerts"].append({"type": "CriticalError", "msg": f"Phát hiện {stats['error_count']} lỗi hệ thống", "runbook": "#L50"})
            
        return stats
    except Exception as e:
        return {"error": str(e)}

@app.get("/runbooks")
async def serve_runbooks():
    """Phục vụ tài liệu hướng dẫn xử lý sự cố dưới dạng HTML đơn giản"""
    root_dir = Path(__file__).parent.parent.parent.parent
    runbook_path = root_dir / "docs" / "runbooks.md"
    if not runbook_path.exists():
        return {"error": f"Runbook file not found at {runbook_path}"}
    
    with open(runbook_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    # Một chút HTML đơn giản để hiển thị Markdown dễ đọc hơn
    html_content = f"""
    <html>
    <head>
        <title>Runbooks | TA Chatbot</title>
        <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@400;600&display=swap" rel="stylesheet">
        <style>
            body {{ font-family: 'Outfit', sans-serif; line-height: 1.6; padding: 2rem; max-width: 800px; margin: 0 auto; background: #0f172a; color: #f8fafc; }}
            h1, h2 {{ color: #38bdf8; border-bottom: 1px solid #1e293b; padding-bottom: 0.5rem; }}
            pre {{ background: #1e293b; padding: 1rem; border-radius: 0.5rem; color: #4ade80; }}
            hr {{ border: 0; border-top: 1px solid #1e293b; margin: 2rem 0; }}
        </style>
    </head>
    <body>{content.replace('\n', '<br>')}</body>
    </html>
    """
    from fastapi.responses import HTMLResponse
    return HTMLResponse(content=html_content)


@app.get("/api/obs/audit")
async def get_audit_logs():
    """Lấy 20 events audit mới nhất cho Dashboard"""
    root_dir = Path(__file__).parent.parent.parent.parent
    audit_file = root_dir / "data" / "audit.jsonl"
    if not audit_file.exists(): return []
    try:
        with open(audit_file, "r", encoding="utf-8") as f:
            lines = f.readlines()
            return [json.loads(l) for l in lines[-20:]][::-1]
    except: return []

@app.get("/obs-dashboard")
async def serve_dashboard():
    """Phục vụ giao diện Dashboard chính"""
    return FileResponse("app/static/obs_dashboard.html")


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
