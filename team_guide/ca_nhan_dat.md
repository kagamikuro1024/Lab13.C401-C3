# 📋 KẾ HOẠCH CÁ NHÂN — ĐẠT
## Day 13: Monitoring, Logging & Observability

> **Nhánh Git cần tạo:** `feature/slo-dat`  
> **Nhiệm vụ chính:** SLO Configuration + Grading Evidence + Validate Logs  
> **Thời gian ước tính:** 60–75 phút

---

## 🎯 Đạt làm gì?

Đạt chịu trách nhiệm **đảm bảo chất lượng** của lab bằng cách:

1. **Cấu hình SLO** (Service Level Objectives) — định nghĩa ngưỡng hiệu năng hệ thống
2. **Chạy validate_logs.py** — công cụ tự động chấm điểm triển khai logging
3. **Điền grading evidence** — tài liệu bằng chứng nộp cho giảng viên
4. **Cập nhật dashboard-spec** — mô tả 6 panels của dashboard

---

## 📂 Các file cần chỉnh sửa

| File | Việc cần làm |
|------|-------------|
| `config/slo.yaml` | Cập nhật giá trị SLO phù hợp với hệ thống |
| `docs/grading-evidence.md` | Điền bằng chứng hoàn thành từng hạng mục |
| `docs/dashboard-spec.md` | Bổ sung mô tả chi tiết 6 panels |

---

## 🔢 TỪNG BƯỚC THỰC HIỆN

### ✅ Bước 1 — Tạo nhánh Git

```bash
git checkout main
git pull origin main
git checkout -b feature/slo-dat
```

---

### ✅ Bước 2 — Cập nhật `config/slo.yaml`

File hiện tại có SLO cơ bản. Đạt sẽ bổ sung giải thích và cập nhật giá trị target thực tế.

**Thay toàn bộ nội dung** file `config/slo.yaml` bằng nội dung sau:

```yaml
# SLO (Service Level Objectives) — Cam kết chất lượng dịch vụ
# Hệ thống: TA_Chatbot — Lab Day 13 Observability
# Cập nhật bởi: Đạt

service: ta-chatbot-day13
# Cửa sổ đo lường: 28 ngày gần nhất (rolling window)
window: 28d

slis:
  # SLI 1: Độ trễ P95 — 95% requests phải hoàn thành dưới ngưỡng này
  latency_p95_ms:
    objective: 3000       # Ngưỡng: dưới 3 giây
    target: 99.5          # Mục tiêu: 99.5% thời gian đạt ngưỡng này
    note: "Đo tại endpoint /chat. Nếu vượt → alert high_latency_p95"

  # SLI 2: Tỷ lệ lỗi — phải dưới 2% tổng số requests
  error_rate_pct:
    objective: 2          # Ngưỡng: không quá 2% lỗi
    target: 99.0          # Mục tiêu: 99% thời gian đạt ngưỡng này
    note: "Tính từ HTTP 5xx responses tại /chat. Nếu vượt → alert high_error_rate"

  # SLI 3: Chi phí hàng ngày — kiểm soát budget LLM
  daily_cost_usd:
    objective: 2.5        # Ngưỡng: không quá $2.5/ngày
    target: 100.0         # Mục tiêu: luôn luôn dưới ngưỡng
    note: "Tính từ tổng token_in + token_out * giá LLM. Nếu vượt → alert cost_budget_spike"

  # SLI 4: Chất lượng câu trả lời — điểm heuristic trung bình
  quality_score_avg:
    objective: 0.75       # Ngưỡng: điểm chất lượng trung bình ≥ 0.75
    target: 95.0          # Mục tiêu: 95% thời gian đạt ngưỡng này
    note: "Điểm từ hàm _heuristic_quality trong agent.py. Nếu thấp → alert low_quality_score"

# Bằng chứng đo lường (điền sau khi chạy validate_logs.py và load_test.py)
evidence:
  measured_latency_p95_ms: ""   # Điền sau khi chạy: curl localhost:8000/metrics
  measured_error_rate_pct: ""   # Điền sau khi chạy load test
  measured_daily_cost_usd: ""   # Điền sau khi chạy load test
  measured_quality_avg: ""      # Điền sau khi chạy load test
  validate_logs_score: ""       # Điền sau khi chạy: python scripts/validate_logs.py
```

**Lưu file.**

---

### ✅ Bước 3 — Chạy App và Lấy Số Liệu

> ⚠️ **Yêu cầu:** App phải đang chạy (Trung hoặc bạn tự khởi động). Nếu chưa chạy:

```bash
# Kích hoạt môi trường ảo
.venv\Scripts\activate

# Khởi động server
uvicorn app.main:app --reload --port 8000
```

**Mở terminal mới** và chạy lệnh sau để sinh dữ liệu:

```bash
# Sinh 20 requests để có metrics thực tế
python scripts/load_test.py --concurrency 3
```

Sau khi load_test chạy xong, lấy số liệu:

```bash
# Lệnh này lấy metrics hiện tại
curl http://localhost:8000/metrics
```

Ghi lại các giá trị:
- `latency_p95` → điền vào `measured_latency_p95_ms` trong `slo.yaml`
- `quality_avg` → điền vào `measured_quality_avg`
- `total_cost_usd` → điền vào `measured_daily_cost_usd`

---

### ✅ Bước 4 — Chạy validate_logs.py

```bash
# Lệnh này kiểm tra chất lượng logging implementation
python scripts/validate_logs.py
```

Script sẽ in ra điểm số và các hạng mục. **Chụp màn hình** hoặc copy kết quả.

> Nếu điểm thấp (dưới 80): báo Trung để fix trước khi nộp.

---

### ✅ Bước 5 — Điền `docs/grading-evidence.md`

Mở file `docs/grading-evidence.md` và **thay toàn bộ nội dung** bằng:

```markdown
# 📊 Bằng Chứng Hoàn Thành — Grading Evidence
## Nhóm: [Điền tên nhóm]
## Cập nhật bởi: Đạt | Ngày: [Điền ngày hôm nay]

---

## A. Implementation Quality (30 điểm)

### A1. Logging & Tracing (10 điểm)

| Hạng mục | Yêu cầu | Kết quả | Đạt/Không |
|----------|---------|---------|-----------|
| JSON schema đúng | Có `ts`, `level`, `event`, `correlation_id` | [Điền sau khi kiểm tra logs.jsonl] | |
| Correlation ID xuyên suốt | Mọi log đều có `correlation_id` | [Điền] | |
| Traces trên Langfuse | ≥ 10 traces | [Điền số lượng] | |
| Trace metadata đầy đủ | Có user_id, session_id, tags | [Điền] | |

**Điểm tự đánh giá A1:** /10

### A2. Dashboard & SLO (10 điểm)

| Hạng mục | Yêu cầu | Kết quả | Đạt/Không |
|----------|---------|---------|-----------|
| Dashboard 6 panels | Đủ 6 panels theo spec | [Điền] | |
| Có đơn vị | ms, %, $, req | [Điền] | |
| SLO table hợp lý | 4 SLIs với target | Hoàn thành trong slo.yaml | ✅ |
| Validate score | ≥ 80/100 | [Điền điểm từ validate_logs.py] | |

**Điểm tự đánh giá A2:** /10

### A3. Alerts & PII (10 điểm)

| Hạng mục | Yêu cầu | Kết quả | Đạt/Không |
|----------|---------|---------|-----------|
| PII redacted hoàn toàn | Không có email/SĐT raw trong logs | [Kiểm tra logs.jsonl] | |
| Alert rules | ≥ 3 rules | 4 rules (Nghĩa đã làm) | ✅ |
| Runbook link | Link hoạt động | docs/alerts.md#... | ✅ |

**Điểm tự đánh giá A3:** /10

---

## B. Validate Logs Score

```
[Paste kết quả từ: python scripts/validate_logs.py]
```

**VALIDATE_LOGS_SCORE: /100**

---

## C. Số liệu hệ thống (đo thực tế)

| Metric | Giá trị đo được | SLO Target | Đạt? |
|--------|----------------|------------|------|
| latency_p50_ms | [Điền] | < 1000ms | |
| latency_p95_ms | [Điền] | < 3000ms | |
| latency_p99_ms | [Điền] | < 5000ms | |
| error_rate_pct | [Điền] | < 2% | |
| total_cost_usd | [Điền] | < $2.5/ngày | |
| quality_avg | [Điền] | ≥ 0.75 | |
| total_traces | [Điền] | ≥ 10 | |
| pii_leaks | 0 | 0 | |

---

## D. Git Evidence

| Thành viên | Nhánh | Commits | PR |
|------------|-------|---------|-----|
| Trung | feature/correlation-logging-trung | [Điền] | [Link] |
| Trung | feature/tracing-trung | [Điền] | [Link] |
| Nghĩa | feature/alerts-nghia | [Điền] | [Link] |
| Đạt | feature/slo-dat | [Điền] | [Link] |
| Vinh | feature/pii-vinh | [Điền] | [Link] |
| Minh | feature/dashboard-minh | [Điền] | [Link] |
```

**Lưu file.**

---

### ✅ Bước 6 — Cập nhật `docs/dashboard-spec.md`

Mở file `docs/dashboard-spec.md` và **thêm nội dung chi tiết** (thêm vào cuối file):

```markdown

---

## Chi Tiết 6 Panels — Cập Nhật Bởi Đạt

### Panel 1: Latency P50/P95/P99
- **Dữ liệu từ:** `GET /metrics` → `latency_p50`, `latency_p95`, `latency_p99`
- **Đơn vị:** milliseconds (ms)
- **SLO line:** P95 = 3000ms (màu đỏ nét đứt)
- **Auto refresh:** 30 giây

### Panel 2: Traffic (Request Count)
- **Dữ liệu từ:** `GET /metrics` → `traffic`
- **Đơn vị:** số requests tích lũy
- **Hiển thị:** Bar chart hoặc line chart theo thời gian

### Panel 3: Error Rate với Breakdown
- **Dữ liệu từ:** `GET /metrics` → `error_breakdown`
- **Đơn vị:** phần trăm (%)
- **SLO line:** Error rate = 2% (màu cam)
- **Breakdown:** Theo loại lỗi (HTTPException, TimeoutError, ...)

### Panel 4: Cost Over Time
- **Dữ liệu từ:** `GET /metrics` → `total_cost_usd`, `avg_cost_usd`
- **Đơn vị:** USD ($)
- **SLO line:** $2.5/ngày
- **Alert threshold:** $0.10/giờ

### Panel 5: Tokens In/Out
- **Dữ liệu từ:** `GET /metrics` → `tokens_in_total`, `tokens_out_total`
- **Đơn vị:** số tokens
- **Tỷ lệ:** tokens_out/tokens_in (hiệu quả LLM)

### Panel 6: Quality Score (Proxy)
- **Dữ liệu từ:** `GET /metrics` → `quality_avg`
- **Đơn vị:** điểm 0.0 – 1.0
- **SLO line:** 0.75 (màu xanh lá)
- **Ý nghĩa:** Điểm heuristic đánh giá chất lượng câu trả lời
```

---

### ✅ Bước 7 — Commit và Push

```bash
# Thêm tất cả file đã sửa vào commit
git add config/slo.yaml docs/grading-evidence.md docs/dashboard-spec.md

# Commit với message mô tả rõ ràng
git commit -m "feat(slo): cập nhật SLO config, grading evidence, dashboard spec chi tiết"

# Push lên GitHub
git push origin feature/slo-dat
```

**Sau khi push:** báo Trung để merge vào `main`.

---

## ✅ CHECKLIST HOÀN THÀNH

- [ ] Đã tạo nhánh `feature/slo-dat`
- [ ] `config/slo.yaml`: Có 4 SLIs với giá trị và giải thích bằng tiếng Việt
- [ ] `config/slo.yaml`: Phần `evidence` đã điền số liệu thực tế
- [ ] `docs/grading-evidence.md`: Điền đầy đủ bảng điểm tự đánh giá
- [ ] `docs/grading-evidence.md`: Có kết quả validate_logs.py
- [ ] `docs/dashboard-spec.md`: Có mô tả chi tiết 6 panels với đơn vị và SLO lines
- [ ] Đã chạy `python scripts/validate_logs.py` và ghi lại điểm
- [ ] Đã commit với message rõ ràng
- [ ] Đã push lên GitHub và báo Trung
