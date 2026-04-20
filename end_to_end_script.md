# 🎬 KỊCH BẢN TỔNG THỂ — TECH LEAD TRUNG
## Day 13: Monitoring, Logging & Observability

> **Người thực hiện:** Trung (Tech Lead)  
> **Thời lượng ước tính:** 4 giờ  
> **Hệ thống mục tiêu:** TA_Chatbot (`app/backend/` + `app/frontend/`) + Template Lab (`app/`)

---

## 📐 SƠ ĐỒ LUỒNG NHÁNH GIT

```
main (Trung quản lý)
├── feature/correlation-logging-trung     ← Trung tự làm
├── feature/tracing-trung                 ← Trung tự làm
├── feature/load-test-trung               ← Trung tự làm
├── feature/alerts-nghia                  ← Nghĩa làm → Trung merge
├── feature/slo-dat                       ← Đạt làm → Trung merge
├── feature/pii-vinh                      ← Vinh làm → Trung merge
└── feature/dashboard-minh                ← Minh làm → Trung merge
```

**Quy tắc merge:**
- Chỉ Trung được merge vào `main`
- Mỗi thành viên push nhánh feature lên GitHub → tạo PR → Trung review → merge
- Không merge nếu `validate_logs.py` chưa pass

---

## 🚀 BƯỚC 0 — CHẠY DEMO LOCAL TRƯỚC KHI LÀM BẤT CỨ THỨ GÌ

> ⚠️ **BẮT BUỘC** — Phải chạy thành công bước này trước khi tiếp tục

### 0.1 — Setup môi trường

```bash
# Tạo virtual environment
python -m venv .venv

# Kích hoạt (Windows)
.venv\Scripts\activate

# Cài dependencies
pip install -r requirements.txt

# Copy file .env
cp .env.example .env
# Mở .env và kiểm tra: APP_NAME, APP_ENV, LOG_PATH
```

### 0.2 — Khởi động app template (FastAPI)

```bash
# Từ thư mục gốc Lab13-Observability/
uvicorn app.main:app --reload --port 8000
```

Mở browser kiểm tra:
- `http://localhost:8000/health` → phải trả về `{"ok": true, ...}`
- `http://localhost:8000/docs` → Swagger UI

### 0.3 — Gửi request thử nghiệm

```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"user_id": "test-001", "message": "Hello world", "feature": "qa", "session_id": "sess-001"}'
```

Kiểm tra: `data/logs.jsonl` phải có bản ghi mới.

⏸️ **[CHECKPOINT 0 — Trung xác nhận app chạy được trước khi tiếp tục]**

---

## 📌 BƯỚC 1 — Tạo nhánh làm việc & Implement Correlation ID

### 1.1 — Tạo nhánh

```bash
git checkout -b feature/correlation-logging-trung
```

### 1.2 — Hoàn thiện `app/middleware.py`

Mở file `app/middleware.py` và thực hiện các TODO:

```python
# Xóa comment TODO, thay bằng code hoàn chỉnh:

async def dispatch(self, request: Request, call_next):
    # Xóa contextvars của request trước để tránh rò rỉ dữ liệu giữa các request
    clear_contextvars()

    # Lấy x-request-id từ header hoặc tự sinh UUID mới
    raw = request.headers.get("x-request-id", "")
    correlation_id = raw if raw else f"req-{uuid.uuid4().hex[:8]}"

    # Gắn correlation_id vào structlog context để log nào cũng có
    bind_contextvars(correlation_id=correlation_id)

    request.state.correlation_id = correlation_id

    start = time.perf_counter()
    response = await call_next(request)
    elapsed_ms = int((time.perf_counter() - start) * 1000)

    # Thêm thông tin vào response headers để client có thể trace
    response.headers["x-request-id"] = correlation_id
    response.headers["x-response-time-ms"] = str(elapsed_ms)

    return response
```

### 1.3 — Hoàn thiện `app/main.py` (Enrich logs)

Mở file `app/main.py`, tại hàm `chat()`, bỏ comment bind_contextvars:

```python
@app.post("/chat", response_model=ChatResponse)
async def chat(request: Request, body: ChatRequest) -> ChatResponse:
    # Làm giàu log với thông tin ngữ cảnh của từng request
    bind_contextvars(
        user_id_hash=hash_user_id(body.user_id),
        session_id=body.session_id,
        feature=body.feature,
        model="claude-sonnet-4-5",   # model mặc định
        env=os.getenv("APP_ENV", "dev"),
    )
    # ... phần còn lại giữ nguyên
```

### 1.4 — Hoàn thiện `app/logging_config.py` (Bật PII scrubber)

```python
def configure_logging() -> None:
    ...
    structlog.configure(
        processors=[
            merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.TimeStamper(fmt="iso", utc=True, key="ts"),
            scrub_event,           # ← Bỏ comment dòng này để bật PII scrubbing
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            JsonlFileProcessor(),
            structlog.processors.JSONRenderer(),
        ],
        ...
    )
```

### 1.5 — Verify & Commit

```bash
# Khởi động lại server
uvicorn app.main:app --reload --port 8000

# Gửi request có PII
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"user_id": "student@example.com", "message": "SĐT em là 0912345678", "feature": "qa", "session_id": "sess-001"}'

# Kiểm tra log: email và SĐT phải bị redact
cat data/logs.jsonl | tail -5

# Kiểm tra correlation_id xuất hiện trong log
cat data/logs.jsonl | python -c "import sys,json; [print(json.loads(l).get('correlation_id','MISSING')) for l in sys.stdin]"
```

```bash
git add app/middleware.py app/main.py app/logging_config.py
git commit -m "feat(logging): hoàn thiện correlation ID middleware và log enrichment"
```

⏸️ **[CHECKPOINT 1 — Trung kiểm tra: correlation_id xuất hiện trong TẤT CẢ log lines, PII bị redact]**

---

## 📌 BƯỚC 2 — Distributed Tracing với Langfuse

### 2.1 — Cấu hình Langfuse

Mở `.env`, thêm:
```
LANGFUSE_PUBLIC_KEY=pk-lf-xxxxxxxx
LANGFUSE_SECRET_KEY=sk-lf-xxxxxxxx
LANGFUSE_HOST=https://cloud.langfuse.com
```

> Nếu chưa có account: đăng ký tại https://cloud.langfuse.com (free tier)

### 2.2 — Kiểm tra tracing đã hoạt động

Tracing đã được cài sẵn trong `app/agent.py` với decorator `@observe()`. Chỉ cần set đúng env var.

```bash
# Kiểm tra
curl http://localhost:8000/health
# Phải thấy: "tracing_enabled": true
```

### 2.3 — Sinh ≥ 10 traces cho Langfuse

```bash
# Chạy script load test nhẹ để tạo traces
python scripts/load_test.py --concurrency 5
```

Sau đó vào https://cloud.langfuse.com → Traces → xác nhận có ít nhất 10 traces.

Mỗi trace phải có:
- `user_id` (đã hash)
- `session_id`
- Tags: `["lab", feature, model]`
- Metadata: `doc_count`, `query_preview`

### 2.4 — Commit

```bash
git add .env.example  # cập nhật example với key mới (không commit .env thật!)
git commit -m "feat(tracing): kích hoạt Langfuse distributed tracing, tags đầy đủ"
```

⏸️ **[CHECKPOINT 2 — Trung xác nhận ≥ 10 traces visible trên Langfuse dashboard]**

---

## 📌 BƯỚC 3 — Load Testing

### 3.1 — Chạy load test

```bash
# Test với concurrency cao để đo P95, P99
python scripts/load_test.py --concurrency 5

# Xem metrics
curl http://localhost:8000/metrics
```

Ghi lại kết quả:
- `latency_p50`, `latency_p95`, `latency_p99`
- `total_cost_usd`
- `quality_avg`

### 3.2 — Commit

```bash
git add .
git commit -m "test(load): chạy load test concurrency=5, ghi nhận metrics baseline"
```

⏸️ **[CHECKPOINT 3 — Trung ghi lại kết quả metrics vào file grading-evidence.md]**

---

## 📌 BƯỚC 4 — Incident Injection & Debugging

### 4.1 — Inject incident RAG slow

```bash
# Mở terminal 2: giữ server chạy ở terminal 1

# Inject sự cố RAG chậm
python scripts/inject_incident.py --scenario rag_slow

# Gửi requests trong khi incident đang bật
python scripts/load_test.py --concurrency 3

# Xem metrics bị ảnh hưởng
curl http://localhost:8000/metrics
```

### 4.2 — Debug bằng Metrics → Traces → Logs

1. **Metrics**: `latency_p95` tăng đột biến
2. **Traces**: Vào Langfuse, tìm trace có latency cao → xem span nào chậm
3. **Logs**: `cat data/logs.jsonl | grep "rag_slow"` hoặc tìm correlation_id của trace đó

### 4.3 — Restore & Commit

```bash
# Tắt incident
python scripts/inject_incident.py --scenario rag_slow --disable

# Commit
git commit -m "test(incident): inject rag_slow, root cause xác định qua traces + logs"
```

⏸️ **[CHECKPOINT 4 — Trung ghi lại root cause vào docs/blueprint-template.md phần Incident Response]**

---

## 📌 BƯỚC 5 — Merge nhánh các thành viên

### 5.1 — Thứ tự merge (theo dependency)

```bash
# 1. Merge Vinh (PII patterns) trước — vì Trung depend vào scrub_event
git checkout main
git merge feature/pii-vinh --no-ff -m "merge: PII patterns enhancement từ Vinh"

# 2. Merge Nghĩa (alerts)
git merge feature/alerts-nghia --no-ff -m "merge: alert rules & runbook từ Nghĩa"

# 3. Merge Đạt (SLO + evidence)
git merge feature/slo-dat --no-ff -m "merge: SLO config & grading evidence từ Đạt"

# 4. Merge Minh (dashboard)
git merge feature/dashboard-minh --no-ff -m "merge: dashboard spec & blueprint report từ Minh"

# 5. Merge nhánh của Trung
git merge feature/correlation-logging-trung --no-ff -m "merge: correlation ID + tracing + load test từ Trung"
```

### 5.2 — Giải quyết conflict (nếu có)

Conflict thường xảy ra ở:
- `requirements.txt` → giữ union tất cả packages
- `data/logs.jsonl` → file output, không nên track bằng git (thêm vào .gitignore)

### 5.3 — Chạy validate_logs.py sau merge

```bash
# Phải đạt ≥ 80/100 để pass
python scripts/validate_logs.py
```

⏸️ **[CHECKPOINT 5 — Trung xác nhận validate_logs.py ≥ 80/100 trên nhánh main]**

---

## 📌 BƯỚC 6 — Hoàn thiện Blueprint Report

### 6.1 — Điền `docs/blueprint-template.md`

Điền đầy đủ các trường:
- `[GROUP_NAME]`: Tên nhóm
- `[REPO_URL]`: Link GitHub repo
- `[MEMBERS]`: Danh sách thành viên + vai trò
- `[VALIDATE_LOGS_FINAL_SCORE]`: Điểm từ validate_logs.py
- `[TOTAL_TRACES_COUNT]`: Số traces trên Langfuse
- `[PII_LEAKS_FOUND]`: Phải là 0
- Phần Incident Response: root cause, fix action

### 6.2 — Commit & Push

```bash
git add docs/blueprint-template.md
git commit -m "docs: hoàn thiện blueprint report, điểm cuối cùng"
git push origin main
```

⏸️ **[CHECKPOINT 6 — HOÀN THÀNH — Trung kiểm tra repo lần cuối trước demo]**

---

## 🎤 BƯỚC 7 — Chuẩn bị Demo

### Thứ tự demo (5–7 phút)

1. **Khởi động** `uvicorn app.main:app --reload` (30 giây)
2. **Gửi chat request** → chỉ `x-request-id` trong response headers (30 giây)
3. **Mở `data/logs.jsonl`** → show correlation_id, PII đã redact (1 phút)
4. **Mở Langfuse** → show trace waterfall (1 phút)
5. **Chạy `python scripts/inject_incident.py --scenario rag_slow`** → show metrics tăng → tìm trace → tìm log (2 phút)
6. **`curl /metrics`** → show 6 panels data (30 giây)
7. **`python scripts/validate_logs.py`** → show điểm cuối cùng (30 giây)

---

## 📋 CHECKLIST CUỐI CÙNG

- [ ] `app/middleware.py` — Correlation ID middleware hoàn chỉnh
- [ ] `app/main.py` — Log enrichment với user_id_hash, session_id, feature
- [ ] `app/logging_config.py` — PII scrubber processor đã bật
- [ ] `app/pii.py` — Có ít nhất 4 PII patterns
- [ ] `data/logs.jsonl` — Mỗi dòng có `correlation_id`, không có PII raw
- [ ] Langfuse — ≥ 10 traces với đầy đủ tags, user_id, session_id
- [ ] `config/alert_rules.yaml` — ≥ 3 alert rules
- [ ] `config/slo.yaml` — SLO table hợp lý
- [ ] `docs/alerts.md` — Runbook đầy đủ
- [ ] `docs/blueprint-template.md` — Điền hoàn chỉnh
- [ ] `scripts/validate_logs.py` — Điểm ≥ 80/100
- [ ] Tất cả nhánh feature đã merge vào `main`
