# 🗓️ KẾ HOẠCH LAB — TRUNG TỰ LÀM ĐỘC LẬP
## Day 13: Monitoring, Logging & Observability

> **Mục đích:** Trung có thể dùng file này để **tự hoàn thành toàn bộ lab** trên máy mình mà **không cần chờ thành viên** commit — đủ điểm rubric để nộp độc lập nếu cần.  
> **Ước tính:** 3.5 – 4 giờ  
> **Chiến lược:** Trung làm song song phần của mình trong khi thành viên làm nhánh feature. Cuối buổi merge lại.

---

## ⚙️ ĐIỀU KIỆN TIÊN QUYẾT

Trước khi bắt đầu, kiểm tra:
- [ ] Python 3.10+ đã cài
- [ ] `git` đã cài và đã `git clone` repo về máy
- [ ] Đang đứng trong thư mục `Lab13-Observability/`

---

## 📋 BẢNG TIẾN ĐỘ TỔNG QUAN

| # | Việc làm | Thời gian | Điểm rubric |
|---|----------|-----------|-------------|
| 0 | Setup môi trường + Demo local | 15 phút | — |
| 1 | Fix middleware (Correlation ID) | 20 phút | A1 |
| 2 | Enrich logs + bật PII scrubber | 20 phút | A1 + A3 |
| 3 | Tăng cường PII patterns | 15 phút | A3 |
| 4 | Cấu hình & verify Langfuse tracing | 20 phút | A1 |
| 5 | Cấu hình alert rules (4 rules) | 15 phút | A3 |
| 6 | Cấu hình SLO | 10 phút | A2 |
| 7 | Chạy validate_logs.py | 10 phút | Passing criteria |
| 8 | Load test (concurrency=5) | 15 phút | A2 |
| 9 | Incident injection + root cause | 20 phút | A2 |
| 10 | Viết runbook + grading evidence | 20 phút | A3 |
| 11 | Tạo dashboard script | 20 phút | A2 |
| 12 | Điền blueprint-template.md | 20 phút | B1 |
| 13 | Cleanup + cuối cùng | 10 phút | — |

---

## 🚀 BƯỚC 0 — SETUP MÔI TRƯỜNG & DEMO LOCAL

**Thời gian:** 15 phút

```bash
# Tạo virtual environment
python -m venv .venv

# Kích hoạt (Windows PowerShell)
.venv\Scripts\activate

# Cài tất cả dependencies
pip install -r requirements.txt

# Copy và kiểm tra .env
cp .env.example .env
# Mở .env, đảm bảo LOG_PATH=data/logs.jsonl và APP_ENV=dev
```

```bash
# Khởi động server
uvicorn app.main:app --reload --port 8000
```

Mở browser, kiểm tra:
- `http://localhost:8000/health` → `{"ok": true, ...}`
- `http://localhost:8000/docs` → Swagger UI hoạt động

```bash
# Test request đầu tiên
curl -X POST http://localhost:8000/chat ^
  -H "Content-Type: application/json" ^
  -d "{\"user_id\": \"trung-001\", \"message\": \"Hello\", \"feature\": \"qa\", \"session_id\": \"sess-001\"}"

# Kiểm tra log đã ghi
type data\logs.jsonl
```

```bash
git add .
git commit -m "chore: setup môi trường, xác nhận app chạy thành công"
```

⏸️ [DỪNG LẠI — Trung kiểm tra: health OK, log đã ghi, trước khi tiếp tục]

---

## 📌 BƯỚC 1 — FIX MIDDLEWARE (CORRELATION ID)

**Thời gian:** 20 phút  
**Nhánh:** `feature/correlation-logging-trung`

```bash
git checkout -b feature/correlation-logging-trung
```

Mở `app/middleware.py`. **Thay toàn bộ nội dung** bằng:

```python
from __future__ import annotations

import time
import uuid

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from structlog.contextvars import bind_contextvars, clear_contextvars


class CorrelationIdMiddleware(BaseHTTPMiddleware):
    """
    Middleware gắn correlation ID vào mỗi request.
    Đảm bảo mọi log trong một request đều có cùng correlation_id để trace.
    """
    async def dispatch(self, request: Request, call_next):
        # Xóa contextvars cũ để tránh rò rỉ dữ liệu giữa các request
        clear_contextvars()

        # Lấy x-request-id từ header hoặc tự sinh UUID mới dạng req-<8-hex>
        raw = request.headers.get("x-request-id", "")
        correlation_id = raw if raw else f"req-{uuid.uuid4().hex[:8]}"

        # Gắn correlation_id vào structlog context — tự động xuất hiện trong TẤT CẢ log
        bind_contextvars(correlation_id=correlation_id)

        # Lưu vào request.state để các handler có thể truy cập
        request.state.correlation_id = correlation_id

        # Đo thời gian xử lý request
        start = time.perf_counter()
        response = await call_next(request)
        elapsed_ms = int((time.perf_counter() - start) * 1000)

        # Trả correlation_id và thời gian xử lý về client qua response headers
        response.headers["x-request-id"] = correlation_id
        response.headers["x-response-time-ms"] = str(elapsed_ms)

        return response
```

Khởi động lại server và verify:

```bash
# Gửi request và xem response headers
curl -v -X POST http://localhost:8000/chat ^
  -H "Content-Type: application/json" ^
  -d "{\"user_id\": \"trung-001\", \"message\": \"Test correlation\", \"feature\": \"qa\", \"session_id\": \"s01\"}" 2>&1 | findstr /i "x-request-id"

# Kiểm tra correlation_id xuất hiện trong log
python -c "import json; [print(json.loads(l).get('correlation_id','MISSING')) for l in open('data/logs.jsonl')]"
```

Kết quả mong đợi: **không có "MISSING"** trong output.

```bash
git add app/middleware.py
git commit -m "feat(middleware): implement correlation ID - clear ctx, generate req-<uuid>, bind structlog, add response headers"
```

⏸️ [DỪNG LẠI — Trung xác nhận: correlation_id xuất hiện trong MỌI dòng log]

---

## 📌 BƯỚC 2 — ENRICH LOGS + BẬT PII SCRUBBER

**Thời gian:** 20 phút

### 2a — Enrich logs trong `app/main.py`

Mở `app/main.py`. Tìm hàm `chat()`, thay dòng comment TODO bằng:

```python
@app.post("/chat", response_model=ChatResponse)
async def chat(request: Request, body: ChatRequest) -> ChatResponse:
    # Làm giàu structlog context: thông tin này tự động xuất hiện trong MỌI log của request này
    bind_contextvars(
        user_id_hash=hash_user_id(body.user_id),
        session_id=body.session_id,
        feature=body.feature,
        model="claude-sonnet-4-5",
        env=os.getenv("APP_ENV", "dev"),
    )
    # ... phần còn lại giữ nguyên
```

### 2b — Bật PII scrubber trong `app/logging_config.py`

Mở `app/logging_config.py`. Tìm dòng bị comment `# scrub_event,` và bỏ comment:

```python
structlog.configure(
    processors=[
        merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso", utc=True, key="ts"),
        scrub_event,           # ← BỎ COMMENT DÒNG NÀY
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        JsonlFileProcessor(),
        structlog.processors.JSONRenderer(),
    ],
    ...
)
```

Verify:

```bash
# Gửi request chứa PII
curl -X POST http://localhost:8000/chat ^
  -H "Content-Type: application/json" ^
  -d "{\"user_id\": \"trung@example.com\", \"message\": \"SĐT tôi là 0912345678\", \"feature\": \"qa\", \"session_id\": \"s01\"}"

# Kiểm tra: phải thấy [REDACTED_EMAIL], [REDACTED_PHONE_VN], KHÔNG có giá trị thật
python -c "import json; [print(json.dumps(json.loads(l), ensure_ascii=False)[:200]) for l in open('data/logs.jsonl')][-3:]"
```

```bash
git add app/main.py app/logging_config.py
git commit -m "feat(logging): enrich logs với user_id_hash/session_id/feature/model/env; bật PII scrubber processor"
```

⏸️ [DỪNG LẠI — Trung xác nhận: log có user_id_hash, feature, model; PII bị redact]

---

## 📌 BƯỚC 3 — TĂNG CƯỜNG PII PATTERNS

**Thời gian:** 15 phút

Mở `app/pii.py`. Thêm 3 patterns mới vào `PII_PATTERNS`:

```python
PII_PATTERNS: dict[str, str] = {
    # --- Patterns gốc ---
    "email": r"[\w\.-]+@[\w\.-]+\.\w+",
    "phone_vn": r"(?:\+84|0)[ \.-]?\d{3}[ \.-]?\d{3}[ \.-]?\d{3,4}",
    "cccd": r"\b\d{12}\b",
    "credit_card": r"\b\d{4}[- ]?\d{4}[- ]?\d{4}[- ]?\d{4}\b",
    # --- Patterns mới bổ sung ---
    # Hộ chiếu Việt Nam: 1 chữ cái HOA + 7 chữ số
    "passport_vn": r"\b[A-Z]\d{7}\b",
    # Mã số thuế cá nhân/doanh nghiệp Việt Nam: 10 hoặc 10-3 chữ số
    "tax_id_vn": r"\b\d{10}(?:-\d{3})?\b",
    # Địa chỉ có từ khóa số nhà + đường/phố
    "address_vn": r"(?:số\s+\d+\s+(?:đường|phố)|(?:đường|phố)\s+[\w\s]+,\s*(?:quận|huyện|phường|xã))",
}
```

```bash
# Test nhanh
python -c "from app.pii import scrub_text; print(scrub_text('Hộ chiếu B1234567, email abc@test.com, SĐT 0987654321'))"
# Kết quả mong đợi: Hộ chiếu [REDACTED_PASSPORT_VN], email [REDACTED_EMAIL], SĐT [REDACTED_PHONE_VN]

git add app/pii.py
git commit -m "feat(pii): thêm passport_vn, tax_id_vn, address_vn patterns - tổng cộng 7 PII patterns"
```

---

## 📌 BƯỚC 4 — CẤU HÌNH & VERIFY LANGFUSE TRACING

**Thời gian:** 20 phút

### 4a — Đăng ký Langfuse (nếu chưa có account)

1. Vào https://cloud.langfuse.com → Sign up free
2. Tạo project mới → lấy `Public Key` và `Secret Key`

### 4b — Cấu hình `.env`

Mở `.env` và thêm:

```
LANGFUSE_PUBLIC_KEY=pk-lf-xxxxxxxxxxxxxxxx
LANGFUSE_SECRET_KEY=sk-lf-xxxxxxxxxxxxxxxx
LANGFUSE_HOST=https://cloud.langfuse.com
```

### 4c — Khởi động lại server và verify

```bash
# Khởi động lại (Ctrl+C trước, rồi chạy lại)
uvicorn app.main:app --reload --port 8000

# Kiểm tra tracing đã bật
curl http://localhost:8000/health
# Phải thấy: "tracing_enabled": true

# Gửi 3 request để tạo traces
curl -X POST http://localhost:8000/chat -H "Content-Type: application/json" -d "{\"user_id\": \"trung-001\", \"message\": \"Con trỏ là gì?\", \"feature\": \"qa\", \"session_id\": \"s01\"}"
curl -X POST http://localhost:8000/chat -H "Content-Type: application/json" -d "{\"user_id\": \"trung-002\", \"message\": \"Vòng lặp for trong C?\", \"feature\": \"qa\", \"session_id\": \"s02\"}"
curl -X POST http://localhost:8000/chat -H "Content-Type: application/json" -d "{\"user_id\": \"trung-003\", \"message\": \"Mảng 2 chiều?\", \"feature\": \"debug\", \"session_id\": \"s03\"}"
```

Vào https://cloud.langfuse.com → Traces → xác nhận traces có:
- `user_id` dạng hash (12 ký tự hex)
- `session_id`
- Tags: `["lab", "qa", "claude-sonnet-4-5"]`

```bash
git add .env.example  # Cập nhật example (KHÔNG commit .env thật)
git commit -m "feat(tracing): cấu hình Langfuse; xác nhận tracing_enabled=true, traces có đủ metadata"
```

⏸️ [DỪNG LẠI — Trung xác nhận ≥ 3 traces visible trên Langfuse với đủ user_id, tags]

---

## 📌 BƯỚC 5 — CẤU HÌNH ALERT RULES (4 RULES)

**Thời gian:** 15 phút

Mở `config/alert_rules.yaml`. Thay toàn bộ nội dung:

```yaml
# Quy tắc cảnh báo — TA_Chatbot Day 13 Lab
# Cập nhật bởi: Trung (và Nghĩa trên nhánh riêng)

alerts:
  # Alert 1: Độ trễ P95 cao
  - name: high_latency_p95
    severity: P2
    description: "P95 latency vượt 5 giây trong 30 phút — hệ thống phản hồi chậm"
    condition: latency_p95_ms > 5000 for 30m
    type: symptom-based
    owner: team-oncall
    runbook: docs/alerts.md#1-high-latency-p95

  # Alert 2: Tỷ lệ lỗi cao (P1 — nghiêm trọng nhất)
  - name: high_error_rate
    severity: P1
    description: "Tỷ lệ lỗi > 5% trong 5 phút — cần xử lý ngay lập tức"
    condition: error_rate_pct > 5 for 5m
    type: symptom-based
    owner: team-oncall
    runbook: docs/alerts.md#2-high-error-rate

  # Alert 3: Chi phí tăng đột biến
  - name: cost_budget_spike
    severity: P2
    description: "Chi phí API tăng gấp đôi baseline trong 15 phút"
    condition: hourly_cost_usd > 2x_baseline for 15m
    type: symptom-based
    owner: finops-owner
    runbook: docs/alerts.md#3-cost-budget-spike

  # Alert 4: Chất lượng câu trả lời xuống thấp
  - name: low_quality_score
    severity: P3
    description: "Quality score TB dưới 0.6 trong 30 phút — chatbot trả lời kém chất lượng"
    condition: quality_score_avg < 0.6 for 30m
    type: symptom-based
    owner: team-oncall
    runbook: docs/alerts.md#4-low-quality-score
```

Mở `docs/alerts.md`. Thay nội dung bằng runbook đầy đủ cho 4 alerts (xem mẫu trong `ca_nhan_nghia.md`).

```bash
git add config/alert_rules.yaml docs/alerts.md
git commit -m "feat(alerts): 4 alert rules với description đầy đủ; runbook 4 mục trong docs/alerts.md"
```

---

## 📌 BƯỚC 6 — CẤU HÌNH SLO

**Thời gian:** 10 phút

Mở `config/slo.yaml`. Thay toàn bộ:

```yaml
# SLO — Service Level Objectives
# Hệ thống TA_Chatbot - Day 13 Lab
service: ta-chatbot-day13
window: 28d

slis:
  latency_p95_ms:
    objective: 3000     # Dưới 3 giây
    target: 99.5
    note: "Đo tại /chat endpoint. Alert: high_latency_p95"
  error_rate_pct:
    objective: 2        # Dưới 2% lỗi
    target: 99.0
    note: "HTTP 5xx / total requests. Alert: high_error_rate"
  daily_cost_usd:
    objective: 2.5      # Dưới $2.5/ngày
    target: 100.0
    note: "Tổng token cost. Alert: cost_budget_spike"
  quality_score_avg:
    objective: 0.75     # Điểm chất lượng ≥ 0.75
    target: 95.0
    note: "Heuristic score từ agent.py. Alert: low_quality_score"
```

```bash
git add config/slo.yaml
git commit -m "feat(slo): cập nhật 4 SLIs với objective, target, note giải thích bằng tiếng Việt"
```

---

## 📌 BƯỚC 7 — CHẠY VALIDATE_LOGS.PY

**Thời gian:** 10 phút

```bash
# Sinh thêm log để validate có dữ liệu
curl -X POST http://localhost:8000/chat -H "Content-Type: application/json" ^
  -d "{\"user_id\": \"student@gmail.com\", \"message\": \"Hàm malloc là gì?\", \"feature\": \"qa\", \"session_id\": \"s-val\"}"
curl -X POST http://localhost:8000/chat -H "Content-Type: application/json" ^
  -d "{\"user_id\": \"user-001\", \"message\": \"Debug pointer error\", \"feature\": \"debug\", \"session_id\": \"s-val2\"}"

# Chạy validate
python scripts/validate_logs.py
```

**Ghi lại điểm số** → nếu < 80: đọc thông báo lỗi và fix.

Các lỗi thường gặp và cách fix:
- `correlation_id missing` → middleware chưa được apply đúng
- `PII found in logs` → `scrub_event` chưa được bật trong `logging_config.py`
- `schema invalid` → thiếu field bắt buộc, kiểm tra `config/logging_schema.json`

```bash
git add data/logs.jsonl
git commit -m "test(validate): chạy validate_logs.py — điểm [ĐIỀN ĐIỂM]/100"
```

⏸️ [DỪNG LẠI — Trung xác nhận validate_logs.py ≥ 80/100 trước khi load test]

---

## 📌 BƯỚC 8 — LOAD TEST

**Thời gian:** 15 phút

```bash
# Chạy load test với concurrency=5
python scripts/load_test.py --concurrency 5

# Ngay sau khi chạy xong, lấy metrics
curl http://localhost:8000/metrics
```

Ghi lại các giá trị quan trọng:
- `latency_p50`, `latency_p95`, `latency_p99` → điền vào `docs/grading-evidence.md`
- `quality_avg` → phải ≥ 0.75
- `total_cost_usd` → chi phí tổng

Trên Langfuse → xác nhận số traces đã tăng.

```bash
git add .
git commit -m "test(load): load test concurrency=5 hoàn thành; ghi nhận metrics baseline"
```

---

## 📌 BƯỚC 9 — INCIDENT INJECTION & ROOT CAUSE

**Thời gian:** 20 phút

### 9a — Inject sự cố

```bash
# Bật incident rag_slow
python scripts/inject_incident.py --scenario rag_slow

# Gửi request khi đang có incident
python scripts/load_test.py --concurrency 3

# Xem metrics bị ảnh hưởng
curl http://localhost:8000/metrics
# latency_p95 phải tăng đáng kể
```

### 9b — Debug theo flow: Metrics → Traces → Logs

**Metrics:** `latency_p95` tăng → biết có vấn đề về latency

**Traces:**
1. Vào Langfuse → filter theo thời gian 5 phút gần nhất
2. Sort by latency → mở trace có latency cao nhất
3. Xem span waterfall → identify span chậm nhất (thường là span `retrieve` hoặc `run`)
4. Copy Trace ID

**Logs:**
```bash
# Tìm log của trace cụ thể bằng correlation_id
# (Lấy correlation_id từ Langfuse trace metadata hoặc từ response header)
python -c "import json; [print(l) for l in open('data/logs.jsonl') if 'rag_slow' in l or json.loads(l).get('latency_ms',0) > 3000]"
```

### 9c — Restore & Commit

```bash
# Tắt incident
python scripts/inject_incident.py --scenario rag_slow --disable

# Verify hệ thống phục hồi
curl http://localhost:8000/health
```

```bash
git add .
git commit -m "test(incident): inject rag_slow → root cause span 'retrieve' chậm → disable → hệ thống phục hồi"
```

⏸️ [DỪNG LẠI — Trung ghi lại Trace ID và root cause để điền vào blueprint-template.md]

---

## 📌 BƯỚC 10 — VIẾT RUNBOOK + GRADING EVIDENCE

**Thời gian:** 20 phút

Điền đầy đủ `docs/grading-evidence.md` (xem mẫu trong `ca_nhan_dat.md`).

Cập nhật `docs/alerts.md` với số liệu thực tế từ incident injection.

```bash
git add docs/grading-evidence.md docs/alerts.md
git commit -m "docs(evidence): điền grading evidence với số liệu thực tế; cập nhật runbook với root cause rag_slow"
```

---

## 📌 BƯỚC 11 — TẠO DASHBOARD SCRIPT

**Thời gian:** 20 phút

Tạo file `scripts/dashboard.py` (xem nội dung chi tiết trong `ca_nhan_minh.md`).

```bash
# Test dashboard
python scripts/dashboard.py --once
```

**Chụp màn hình** terminal output → dùng làm bằng chứng `[DASHBOARD_6_PANELS_SCREENSHOT]`.

```bash
git add scripts/dashboard.py
git commit -m "feat(dashboard): tạo script dashboard 6 panels với SLO threshold, auto-refresh, ASCII progress bars"
```

---

## 📌 BƯỚC 12 — ĐIỀN BLUEPRINT-TEMPLATE.MD

**Thời gian:** 20 phút

Mở `docs/blueprint-template.md` và điền đầy đủ tất cả các trường `[BRACKET]`.

Các trường quan trọng nhất:
- `[GROUP_NAME]`, `[REPO_URL]`, `[MEMBERS]`
- `[VALIDATE_LOGS_FINAL_SCORE]` → lấy từ bước 7
- `[TOTAL_TRACES_COUNT]` → đếm trên Langfuse
- `[PII_LEAKS_FOUND]` → phải là `0`
- `[SCENARIO_NAME]` → `rag_slow`
- `[ROOT_CAUSE_PROVED_BY]` → Trace ID + Log line từ bước 9

```bash
git add docs/blueprint-template.md
git commit -m "docs(blueprint): hoàn thiện báo cáo nhóm - điền đủ tất cả trường, incident response chi tiết"
```

⏸️ [DỪNG LẠI — Trung review lại toàn bộ blueprint trước khi merge]

---

## 📌 BƯỚC 13 — SINH ≥ 10 TRACES & FINAL CLEANUP

**Thời gian:** 10 phút

```bash
# Đảm bảo có đủ ≥ 10 traces trên Langfuse
python scripts/load_test.py --concurrency 5

# Chạy validate lần cuối
python scripts/validate_logs.py

# Kiểm tra git log sạch
git log --oneline -15
```

```bash
# Merge nhánh của Trung vào main
git checkout main
git merge feature/correlation-logging-trung --no-ff -m "merge: correlation ID, logging, PII, tracing, load test từ Trung"

# Push main lên GitHub
git push origin main
```

⏸️ [DỪNG LẠI — HOÀN THÀNH — Trung kiểm tra lần cuối trước demo]

---

## 🎤 CHECKLIST CUỐI CÙNG TRƯỚC DEMO

```
VALIDATE_LOGS_SCORE  ≥ 80/100   →  python scripts/validate_logs.py
LANGFUSE TRACES      ≥ 10       →  https://cloud.langfuse.com
PII_LEAKS_FOUND      = 0        →  cat data/logs.jsonl | findstr "@"
DASHBOARD            OK         →  python scripts/dashboard.py --once
ALERT RULES          ≥ 3 rules  →  type config\alert_rules.yaml
BLUEPRINT            Filled     →  docs/blueprint-template.md
ALL BRANCHES MERGED  ✅         →  git log --graph --oneline -10
```

---

## 🆘 XỬ LÝ SỰ CỐ THƯỜNG GẶP

| Sự cố | Nguyên nhân | Fix |
|-------|-------------|-----|
| `ModuleNotFoundError: app` | Chưa kích hoạt venv | `.venv\Scripts\activate` |
| `correlation_id: MISSING` | Middleware chưa fix | Bước 1 |
| PII vẫn lọt ra log | `scrub_event` chưa bật | Bước 2b |
| `tracing_enabled: false` | `.env` thiếu LANGFUSE keys | Bước 4b |
| `validate_logs` dưới 80 | Xem chi tiết từng hạng mục | Fix theo lỗi báo |
| Server port 8000 bị chiếm | Tiến trình cũ còn chạy | `netstat -ano \| findstr 8000` |
