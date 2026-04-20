# 📋 KẾ HOẠCH CÁ NHÂN — NGHĨA
## Day 13: Monitoring, Logging & Observability
### Hệ thống: TA_Chatbot (Backend: `app/backend/`)

> **Nhánh Git cần tạo:** `feature/alerts-nghia`  
> **Nhiệm vụ chính:** Cấu hình Alert Rules & Viết Runbook cho chatbot thật  
> **Thời gian ước tính:** 45 phút

---

## 🎯 Nghĩa làm gì?

Trong bài lab, chúng ta cần chứng minh hệ thống có khả năng tự cảnh báo khi có sự cố. Nghĩa sẽ thiết lập các "ngưỡng báo động" (Alert Rules) và viết hướng dẫn cách xử lý (Runbook).

Nhiệm vụ:
1. Hoàn thiện 4 quy tắc cảnh báo trong `config/alert_rules.yaml`.
2. Viết hướng dẫn xử lý sự cố trong `docs/alerts.md`.

---

## 📂 Các file cần chỉnh sửa

| File | Việc cần làm |
|------|-------------|
| `config/alert_rules.yaml` | Thêm mô tả và điều kiện cho 4 cảnh báo: Độ trễ, Tỷ lệ lỗi, Chi phí, Chất lượng |
| `docs/alerts.md` | Viết nội dung Runbook cho chatbot thật |

---

## 🔢 TỪNG BƯỚC THỰC HIỆN

### ✅ Bước 1 — Tạo nhánh Git

```bash
git checkout main
git pull origin main
git checkout -b feature/alerts-nghia
```

---

### ✅ Bước 2 — Cập nhật `config/alert_rules.yaml`

Mở file và thay bằng nội dung chuẩn cho TA_Chatbot:

```yaml
alerts:
  - name: high_latency_p95
    severity: P2
    description: "P95 latency vượt 5 giây - Hệ thống chatbot phản hồi quá chậm"
    condition: latency_p95_ms > 5000 for 30m
    runbook: docs/alerts.md#1-high-latency-p95

  - name: high_error_rate
    severity: P1
    description: "Tỷ lệ lỗi > 5% - Nghi ngờ lỗi API Key hoặc server backend tèo"
    condition: error_rate_pct > 5 for 5m
    runbook: docs/alerts.md#2-high-error-rate

  - name: cost_budget_spike
    severity: P2
    description: "Chi phí OpenAI tăng vọt bất thường"
    condition: hourly_cost_usd > 2x_baseline for 15m
    runbook: docs/alerts.md#3-cost-budget-spike

  - name: low_quality_score
    severity: P3
    description: "Chất lượng câu trả lời chatbot đi xuống (điểm < 0.6)"
    condition: quality_score_avg < 0.6 for 30m
    runbook: docs/alerts.md#4-low-quality-score
```

---

### ✅ Bước 3 — Cập nhật Runbook `docs/alerts.md`

Nghĩa viết hướng dẫn xử lý cụ thể cho chatbot:

```markdown
# 📖 Runbook Xử Lý Sự Cố Chatbot

## 1. HIGH LATENCY P95 (Chatbot chậm)
- **Kiểm tra**: Xem Langfuse traces để biết RAG hay LLM chậm.
- **Xử lý**: Nếu là RAG, kiểm tra FAISS index. Nếu là LLM, có thể OpenAI đang lag.

## 2. HIGH ERROR RATE (Chatbot lỗi)
- **Kiểm tra**: `cat data/logs.jsonl | grep "error"`.
- **Xử lý**: Kiểm tra lại file `.env` đã có OpenAI Key chưa. Kiểm tra internet.

## 3. COST BUDGET SPIKE (Chi phí tăng)
- **Kiểm tra**: `/obs-metrics` để xem `total_cost_usd`.
- **Xử lý**: Dừng ngay nếu có script load test đang chạy quá đà.

## 4. LOW QUALITY SCORE (Trả lời dở)
- **Kiểm tra**: Xem lại prompt trong `agent.py` hoặc dữ liệu `knowledge_base/`.
- **Xử lý**: Cập nhật thêm thông tin vào file `.json` hoặc `.md` trong knowledge base.
```

---

### ✅ Bước 4 — Commit & Push

```bash
git add config/alert_rules.yaml docs/alerts.md
git commit -m "feat(alerts): thêm 4 alert rules và runbook cho chatbot"
git push origin feature/alerts-nghia
```
