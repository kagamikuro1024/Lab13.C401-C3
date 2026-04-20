# 📋 KẾ HOẠCH CÁ NHÂN — MINH
## Day 13: Monitoring, Logging & Observability

> **Nhánh Git cần tạo:** `feature/dashboard-minh`  
> **Nhiệm vụ chính:** Dashboard Implementation + Blueprint Report  
> **Thời gian ước tính:** 75–90 phút

---

## 🎯 Minh làm gì?

Minh chịu trách nhiệm **trực quan hóa dữ liệu** và **hoàn thiện báo cáo nhóm**:

1. **Tạo dashboard** in-process (script Python tạo báo cáo metrics dạng text/HTML)
2. **Điền blueprint-template.md** — báo cáo chính thức của nhóm
3. **Tạo mock-debug-qa.md** — chuẩn bị câu hỏi & đáp án cho phần demo

---

## 📂 Các file cần tạo / chỉnh sửa

| File | Việc cần làm |
|------|-------------|
| `scripts/dashboard.py` | Tạo mới: script in dashboard 6 panels ra terminal |
| `docs/blueprint-template.md` | Điền hoàn chỉnh báo cáo nhóm |
| `docs/mock-debug-qa.md` | Tạo Q&A cho phần demo oral |

---

## 🔢 TỪNG BƯỚC THỰC HIỆN

### ✅ Bước 1 — Tạo nhánh Git

```bash
git checkout main
git pull origin main
git checkout -b feature/dashboard-minh
```

---

### ✅ Bước 2 — Tạo `scripts/dashboard.py`

Script này kết nối vào API `GET /metrics` và in ra dashboard 6 panels dạng text đẹp trong terminal.

Tạo file mới `scripts/dashboard.py` với nội dung:

```python
"""
Script hiển thị dashboard 6 panels — Day 13 Observability Lab
Tác giả: Minh
Chạy: python scripts/dashboard.py
Yêu cầu: server đang chạy tại http://localhost:8000
"""
import time
import json
import sys

try:
    import requests
except ImportError:
    print("Cài đặt thư viện requests trước: pip install requests")
    sys.exit(1)

BASE_URL = "http://localhost:8000"

# Ngưỡng SLO — dùng để hiển thị cảnh báo
SLO = {
    "latency_p95_ms": 3000,   # ms
    "error_rate_pct": 2.0,    # %
    "daily_cost_usd": 2.5,    # USD
    "quality_avg": 0.75,      # điểm 0-1
}


def get_metrics() -> dict:
    """Lấy metrics từ API server"""
    try:
        response = requests.get(f"{BASE_URL}/metrics", timeout=5)
        response.raise_for_status()
        return response.json()
    except requests.ConnectionError:
        print(f"❌ Không kết nối được server tại {BASE_URL}")
        print("   Hãy khởi động server: uvicorn app.main:app --reload")
        sys.exit(1)


def get_health() -> dict:
    """Lấy thông tin health từ API server"""
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        return response.json()
    except Exception:
        return {}


def format_slo_status(value: float, threshold: float, higher_is_better: bool = False) -> str:
    """Trả về emoji trạng thái SLO: ✅ đạt, ❌ vi phạm"""
    if higher_is_better:
        return "✅ ĐẠT" if value >= threshold else "❌ VI PHẠM"
    else:
        return "✅ ĐẠT" if value <= threshold else "❌ VI PHẠM"


def render_bar(value: float, max_value: float, width: int = 20) -> str:
    """Vẽ thanh progress bar đơn giản bằng ký tự ASCII"""
    if max_value == 0:
        return "[" + " " * width + "]"
    filled = int((value / max_value) * width)
    filled = min(filled, width)
    return "[" + "█" * filled + "░" * (width - filled) + "]"


def print_dashboard(metrics: dict, health: dict) -> None:
    """In dashboard 6 panels ra terminal"""
    separator = "─" * 65

    print("\n" + "═" * 65)
    print("  📊  TA_CHATBOT OBSERVABILITY DASHBOARD  —  DAY 13 LAB")
    print("═" * 65)
    print(f"  🕐 Thời gian: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"  🟢 Tracing: {'BẬT' if health.get('tracing_enabled') else 'TẮT'}")
    print(f"  ⚠️  Incidents: {health.get('incidents', {})}")
    print(separator)

    # ─── PANEL 1: LATENCY ───────────────────────────────────────────
    print("\n  📌 PANEL 1 — ĐỘ TRỄ (Latency)")
    p50 = metrics.get("latency_p50", 0)
    p95 = metrics.get("latency_p95", 0)
    p99 = metrics.get("latency_p99", 0)
    slo_status = format_slo_status(p95, SLO["latency_p95_ms"])
    print(f"     P50: {p50:>8.0f} ms  {render_bar(p50, 5000)}")
    print(f"     P95: {p95:>8.0f} ms  {render_bar(p95, 5000)}  [{slo_status}] (SLO: <{SLO['latency_p95_ms']}ms)")
    print(f"     P99: {p99:>8.0f} ms  {render_bar(p99, 5000)}")
    print(separator)

    # ─── PANEL 2: TRAFFIC ───────────────────────────────────────────
    print("\n  📌 PANEL 2 — LƯU LƯỢNG (Traffic)")
    traffic = metrics.get("traffic", 0)
    print(f"     Tổng requests:  {traffic:>6} req")
    print(f"     {render_bar(traffic, max(traffic * 2, 100), 40)}")
    print(separator)

    # ─── PANEL 3: ERROR RATE ────────────────────────────────────────
    print("\n  📌 PANEL 3 — TỶ LỆ LỖI (Error Rate)")
    error_breakdown = metrics.get("error_breakdown", {})
    total_errors = sum(error_breakdown.values())
    error_rate = (total_errors / traffic * 100) if traffic > 0 else 0
    slo_status = format_slo_status(error_rate, SLO["error_rate_pct"])
    print(f"     Tỷ lệ lỗi:  {error_rate:>6.2f} %  [{slo_status}] (SLO: <{SLO['error_rate_pct']}%)")
    print(f"     Tổng lỗi:   {total_errors:>6} errors")
    if error_breakdown:
        print("     Breakdown:")
        for err_type, count in error_breakdown.items():
            print(f"       - {err_type}: {count}")
    else:
        print("     Breakdown: Không có lỗi ✅")
    print(separator)

    # ─── PANEL 4: COST ──────────────────────────────────────────────
    print("\n  📌 PANEL 4 — CHI PHÍ (Cost)")
    total_cost = metrics.get("total_cost_usd", 0)
    avg_cost = metrics.get("avg_cost_usd", 0)
    slo_status = format_slo_status(total_cost, SLO["daily_cost_usd"])
    print(f"     Tổng chi phí:  ${total_cost:>8.4f}  [{slo_status}] (SLO: <${SLO['daily_cost_usd']}/ngày)")
    print(f"     Chi phí TB/req: ${avg_cost:>7.4f}")
    print(f"     {render_bar(total_cost, SLO['daily_cost_usd'] * 2, 40)}")
    print(separator)

    # ─── PANEL 5: TOKENS ────────────────────────────────────────────
    print("\n  📌 PANEL 5 — TOKEN USAGE")
    tokens_in = metrics.get("tokens_in_total", 0)
    tokens_out = metrics.get("tokens_out_total", 0)
    ratio = (tokens_out / tokens_in) if tokens_in > 0 else 0
    print(f"     Tokens IN:   {tokens_in:>8,} tokens")
    print(f"     Tokens OUT:  {tokens_out:>8,} tokens")
    print(f"     Tỷ lệ OUT/IN:  {ratio:>6.2f}x")
    print(separator)

    # ─── PANEL 6: QUALITY ───────────────────────────────────────────
    print("\n  📌 PANEL 6 — CHẤT LƯỢNG (Quality Score)")
    quality = metrics.get("quality_avg", 0)
    slo_status = format_slo_status(quality, SLO["quality_avg"], higher_is_better=True)
    print(f"     Quality avg:  {quality:>6.4f}  [{slo_status}] (SLO: >={SLO['quality_avg']})")
    print(f"     {render_bar(quality, 1.0, 40)}")
    print("\n" + "═" * 65 + "\n")


def main():
    """Vòng lặp chính: tự động refresh dashboard mỗi 30 giây"""
    import argparse
    parser = argparse.ArgumentParser(description="Dashboard 6 panels cho TA_Chatbot")
    parser.add_argument(
        "--once", action="store_true",
        help="Chỉ in 1 lần rồi thoát (mặc định: auto-refresh 30 giây)"
    )
    parser.add_argument(
        "--interval", type=int, default=30,
        help="Khoảng cách refresh tính bằng giây (mặc định: 30)"
    )
    args = parser.parse_args()

    print(f"📡 Kết nối tới {BASE_URL}...")
    metrics = get_metrics()
    health = get_health()
    print_dashboard(metrics, health)

    if args.once:
        return

    print(f"🔄 Tự động refresh mỗi {args.interval} giây. Nhấn Ctrl+C để thoát.\n")
    try:
        while True:
            time.sleep(args.interval)
            metrics = get_metrics()
            health = get_health()
            print_dashboard(metrics, health)
    except KeyboardInterrupt:
        print("\n👋 Đã thoát dashboard.")


if __name__ == "__main__":
    main()
```

**Lưu file.**

---

### ✅ Bước 3 — Test Dashboard Script

```bash
# Đảm bảo server đang chạy (terminal khác)
# uvicorn app.main:app --reload --port 8000

# Trong 1 request để có data
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d "{\"user_id\": \"minh-001\", \"message\": \"Con trỏ là gì?\", \"feature\": \"qa\", \"session_id\": \"sess-minh\"}"

# Chạy dashboard 1 lần
python scripts/dashboard.py --once

# Chạy auto-refresh (Ctrl+C để thoát)
python scripts/dashboard.py --interval 15
```

---

### ✅ Bước 4 — Điền `docs/blueprint-template.md`

Mở file `docs/blueprint-template.md` và điền đầy đủ (Minh điền phần nhóm, cộng tác với các thành viên để điền phần cá nhân):

```markdown
# Day 13 Observability Lab Report

## 1. Team Metadata
- [GROUP_NAME]: Nhóm [Điền số nhóm]
- [REPO_URL]: https://github.com/[username]/Lab13-Observability
- [MEMBERS]:
  - Member A: Trung | Role: Tech Lead — Correlation ID, Logging, Tracing, Load Test, Incident
  - Member B: Nghĩa | Role: Alerts & Runbook
  - Member C: Đạt | Role: SLO & Grading Evidence
  - Member D: Vinh | Role: PII Enhancement & Testing
  - Member E: Minh | Role: Dashboard & Blueprint Report

## 2. Group Performance (Auto-Verified)
- [VALIDATE_LOGS_FINAL_SCORE]: [Điền điểm từ validate_logs.py]/100
- [TOTAL_TRACES_COUNT]: [Điền số traces trên Langfuse]
- [PII_LEAKS_FOUND]: 0

## 3. Technical Evidence (Group)

### 3.1 Logging & Tracing
- [EVIDENCE_CORRELATION_ID_SCREENSHOT]: [Chụp terminal hiển thị logs.jsonl có correlation_id]
- [EVIDENCE_PII_REDACTION_SCREENSHOT]: [Chụp log hiển thị [REDACTED_EMAIL] thay vì email thật]
- [EVIDENCE_TRACE_WATERFALL_SCREENSHOT]: [Chụp màn hình Langfuse trace waterfall]
- [TRACE_WATERFALL_EXPLANATION]: "Span 'retrieve' trong trace waterfall cho thấy RAG retrieval mất khoảng Xms — đây là bottleneck chính khi inject sự cố rag_slow"

### 3.2 Dashboard & SLOs
- [DASHBOARD_6_PANELS_SCREENSHOT]: [Chụp màn hình terminal khi chạy python scripts/dashboard.py]
- [SLO_TABLE]:
| SLI | Target | Window | Current Value |
|---|---:|---|---:|
| Latency P95 | <3000ms | 28d | [Điền] ms |
| Error Rate | <2% | 28d | [Điền] % |
| Cost Budget | <$2.5/day | 1d | $[Điền] |
| Quality Score | ≥0.75 | 28d | [Điền] |

### 3.3 Alerts & Runbook
- [ALERT_RULES_SCREENSHOT]: [Chụp màn hình file config/alert_rules.yaml]
- [SAMPLE_RUNBOOK_LINK]: docs/alerts.md#2-high-error-rate

## 4. Incident Response (Group)
- [SCENARIO_NAME]: rag_slow
- [SYMPTOMS_OBSERVED]: latency_p95 tăng đột biến lên >5000ms, logs hiển thị request_failed với error chậm từ RAG
- [ROOT_CAUSE_PROVED_BY]: Trace ID [Điền ID] trên Langfuse — span 'retrieve' chiếm >90% tổng latency; Log line "request_received" với correlation_id [Điền] cho thấy response time >5000ms
- [FIX_ACTION]: Gọi `python scripts/inject_incident.py --scenario rag_slow --disable`
- [PREVENTIVE_MEASURE]: Thêm timeout 3s cho RAG retrieval; alert high_latency_p95 kích hoạt sau 30 phút để phát hiện sớm

## 5. Individual Contributions & Evidence

### Trung (Tech Lead)
- [TASKS_COMPLETED]: Correlation ID middleware, Log enrichment, PII scrubber activation, Langfuse tracing, Load test, Incident injection, Merge all PRs
- [EVIDENCE_LINK]: [Link commit middleware.py], [Link commit main.py]

### Nghĩa
- [TASKS_COMPLETED]: alert_rules.yaml (4 rules), docs/alerts.md (4 runbooks)
- [EVIDENCE_LINK]: [Link PR feature/alerts-nghia]

### Đạt
- [TASKS_COMPLETED]: config/slo.yaml (4 SLIs), docs/grading-evidence.md, docs/dashboard-spec.md
- [EVIDENCE_LINK]: [Link PR feature/slo-dat]

### Vinh
- [TASKS_COMPLETED]: app/pii.py (+3 patterns), tests/test_pii.py (unit tests)
- [EVIDENCE_LINK]: [Link PR feature/pii-vinh]

### Minh
- [TASKS_COMPLETED]: scripts/dashboard.py (6-panel dashboard), docs/blueprint-template.md
- [EVIDENCE_LINK]: [Link PR feature/dashboard-minh]

## 6. Bonus Items (Optional)
- [BONUS_COST_OPTIMIZATION]: Theo dõi avg_cost_usd qua /metrics; Dashboard panel 4 hiển thị xu hướng chi phí để phát hiện spike sớm
- [BONUS_AUDIT_LOGS]: [Nếu có thêm audit log]
- [BONUS_CUSTOM_METRIC]: Dashboard script tự xây dựng (scripts/dashboard.py) — auto-refresh, SLO status, ASCII progress bars
```

**Lưu file.**

---

### ✅ Bước 5 — Tạo `docs/mock-debug-qa.md`

Kiểm tra xem file này đã có chưa. Nếu chưa, tạo mới:

```bash
# Kiểm tra
dir docs\
```

Tạo file `docs/mock-debug-qa.md`:

```markdown
# 🎤 Mock Debug Q&A — Chuẩn Bị Cho Demo
## Day 13 Observability Lab

> Tài liệu này giúp nhóm chuẩn bị trả lời câu hỏi từ giảng viên trong phần demo.
> Cập nhật bởi: Minh

---

## Q1: Correlation ID hoạt động như thế nào?

**Trả lời:**
Mỗi request vào `/chat` đều đi qua `CorrelationIdMiddleware`. Middleware sẽ:
1. Kiểm tra xem request header có `x-request-id` không. Nếu có → dùng luôn (để client có thể trace).
2. Nếu không có → tự sinh UUID mới dạng `req-<8-hex-chars>`
3. Gắn `correlation_id` vào structlog contextvar để **mọi log trong request đó** đều tự động có field này
4. Trả về `correlation_id` trong response header `x-request-id`

**Demo:** `cat data/logs.jsonl | head -10` → thấy cùng correlation_id trong request_received và response_sent

---

## Q2: PII scrubbing hoạt động ở đâu trong pipeline?

**Trả lời:**
PII scrubbing hoạt động ở 2 tầng:
1. **Trong `pii.py`**: `scrub_text()` sử dụng regex để redact trước khi truyền vào log
2. **Trong `logging_config.py`**: `scrub_event()` là structlog processor — chạy trên **toàn bộ payload** trước khi ghi vào `logs.jsonl`

**Demo:** Gửi request với email → `cat data/logs.jsonl | tail -3` → không thấy email thật

---

## Q3: Làm thế nào để tìm ra root cause của rag_slow?

**Trả lời:** Theo flow Metrics → Traces → Logs:
1. **Metrics**: `/metrics` → `latency_p95` tăng đột biến (>5000ms) → biết có sự cố latency
2. **Traces**: Vào Langfuse → filter traces theo thời gian → mở trace có latency cao → xem span waterfall → phát hiện span `retrieve` chiếm >90% thời gian
3. **Logs**: Lấy `correlation_id` từ trace → `grep correlation_id data/logs.jsonl` → xác nhận độ trễ

---

## Q4: Dashboard có bao nhiêu panels và mỗi panel đo gì?

**Trả lời:** 6 panels:
1. **Latency P50/P95/P99** — đo độ trễ phản hồi (ms), có SLO line
2. **Traffic** — tổng số requests
3. **Error Rate** — tỷ lệ lỗi (%), có SLO line 2%
4. **Cost** — tổng chi phí USD, có SLO line $2.5/ngày
5. **Tokens In/Out** — lượng token tiêu thụ
6. **Quality Score** — điểm heuristic chất lượng câu trả lời, có SLO line 0.75

---

## Q5: Tại sao dùng structlog thay vì logging chuẩn Python?

**Trả lời:**
- `structlog` sinh log dạng **JSON có cấu trúc** thay vì plaintext → dễ parse tự động
- Hỗ trợ **contextvars** — một lần `bind_contextvars(correlation_id=x)` → toàn bộ log trong request tự có field đó
- **Processor pipeline** — có thể thêm bước PII scrubbing, timestamping, filtering mà không sửa code business logic
- Tích hợp tốt với logging chuẩn Python
```

**Lưu file.**

---

### ✅ Bước 6 — Commit và Push

```bash
git add scripts/dashboard.py docs/blueprint-template.md docs/mock-debug-qa.md
git commit -m "feat(dashboard): tạo dashboard 6-panel script; hoàn thiện blueprint report và mock Q&A demo"
git push origin feature/dashboard-minh
```

**Sau khi push:** báo Trung để merge vào `main`.

---

## ✅ CHECKLIST HOÀN THÀNH

- [ ] Đã tạo nhánh `feature/dashboard-minh`
- [ ] `scripts/dashboard.py`: Script hoạt động, in được 6 panels
- [ ] `scripts/dashboard.py`: Mỗi panel có SLO threshold và status (ĐẠT/VI PHẠM)
- [ ] Đã test dashboard: `python scripts/dashboard.py --once` chạy thành công
- [ ] `docs/blueprint-template.md`: Điền đầy đủ Team Metadata, Group Performance, SLO table, Incident Response
- [ ] `docs/mock-debug-qa.md`: Có ≥ 5 câu hỏi & đáp án chuẩn bị cho demo
- [ ] Đã commit với message rõ ràng
- [ ] Đã push lên GitHub và báo Trung
