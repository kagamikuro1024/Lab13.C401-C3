# 📋 KẾ HOẠCH CÁ NHÂN — NGHĨA
## Day 13: Monitoring, Logging & Observability

> **Nhánh Git cần tạo:** `feature/alerts-nghia`  
> **Nhiệm vụ chính:** Cấu hình Alert Rules & Viết Runbook  
> **Thời gian ước tính:** 45–60 phút

---

## 🎯 Nghĩa làm gì?

Bài lab này cần có ít nhất **3 alert rules** (quy tắc cảnh báo) và **1 runbook** (hướng dẫn xử lý sự cố). Nghĩa sẽ:

1. Mở file `config/alert_rules.yaml` → thêm 1 alert rule mới (hiện có 3, cần đủ 3+ và viết đầy đủ hơn)
2. Mở file `docs/alerts.md` → viết nội dung runbook chi tiết

> 💡 **Runbook** là tài liệu hướng dẫn: "Khi hệ thống bị cảnh báo X, thì làm gì?"

---

## 📂 Các file cần chỉnh sửa

| File | Việc cần làm |
|------|-------------|
| `config/alert_rules.yaml` | Thêm 1 alert rule mới (low_quality_score), bổ sung trường `description` cho tất cả |
| `docs/alerts.md` | Viết nội dung runbook cho 4 alert rules |

---

## 🔢 TỪNG BƯỚC THỰC HIỆN

### ✅ Bước 1 — Tạo nhánh Git

Mở terminal (Command Prompt hoặc Git Bash), gõ từng lệnh sau:

```bash
# Lệnh này chuyển sang nhánh main trước
git checkout main

# Lệnh này tải về code mới nhất từ GitHub
git pull origin main

# Lệnh này tạo nhánh mới cho Nghĩa
git checkout -b feature/alerts-nghia
```

> 💡 Sau khi gõ lệnh cuối, terminal sẽ hiện: `Switched to a new branch 'feature/alerts-nghia'` — đó là đúng rồi.

---

### ✅ Bước 2 — Mở và chỉnh sửa file `config/alert_rules.yaml`

**Mở file** `config/alert_rules.yaml` bằng VS Code hoặc Notepad.

**Nội dung hiện tại** của file trông như thế này:
```yaml
alerts:
  - name: high_latency_p95
    ...
  - name: high_error_rate
    ...
  - name: cost_budget_spike
    ...
```

**Thay toàn bộ nội dung** file bằng nội dung sau (copy nguyên, không thêm bớt):

```yaml
# Quy tắc cảnh báo cho hệ thống TA_Chatbot - Lab Day 13
# Mỗi alert có: tên, mức độ nghiêm trọng, điều kiện kích hoạt, runbook

alerts:
  # Cảnh báo 1: Độ trễ P95 cao (hệ thống chậm)
  - name: high_latency_p95
    severity: P2
    description: "Độ trễ P95 vượt ngưỡng 5 giây - hệ thống phản hồi chậm bất thường"
    condition: latency_p95_ms > 5000 for 30m
    type: symptom-based
    owner: team-oncall
    runbook: docs/alerts.md#1-high-latency-p95

  # Cảnh báo 2: Tỷ lệ lỗi cao (nhiều request bị fail)
  - name: high_error_rate
    severity: P1
    description: "Tỷ lệ lỗi vượt 5% trong 5 phút - cần xử lý ngay"
    condition: error_rate_pct > 5 for 5m
    type: symptom-based
    owner: team-oncall
    runbook: docs/alerts.md#2-high-error-rate

  # Cảnh báo 3: Chi phí API tăng đột biến
  - name: cost_budget_spike
    severity: P2
    description: "Chi phí API tăng gấp đôi baseline trong 15 phút - có thể bị tấn công hoặc bug"
    condition: hourly_cost_usd > 2x_baseline for 15m
    type: symptom-based
    owner: finops-owner
    runbook: docs/alerts.md#3-cost-budget-spike

  # Cảnh báo 4: Chất lượng câu trả lời thấp (DO NGHĨA THÊM)
  - name: low_quality_score
    severity: P3
    description: "Điểm chất lượng trung bình giảm dưới 0.6 trong 30 phút - chatbot trả lời kém"
    condition: quality_score_avg < 0.6 for 30m
    type: symptom-based
    owner: team-oncall
    runbook: docs/alerts.md#4-low-quality-score
```

**Lưu file** (Ctrl+S).

---

### ✅ Bước 3 — Mở và chỉnh sửa file `docs/alerts.md`

**Mở file** `docs/alerts.md`. File này hiện còn trống/sơ sài.

**Thay toàn bộ nội dung** bằng nội dung sau:

```markdown
# 📖 Runbook — Hướng Dẫn Xử Lý Sự Cố
## Hệ thống TA_Chatbot - Day 13 Observability Lab

> **Mục đích:** Khi hệ thống gửi cảnh báo (alert), thành viên on-call đọc runbook này để biết phải làm gì.

---

## 1. HIGH LATENCY P95

**Mô tả:** Độ trễ P95 vượt 5000ms trong 30 phút liên tục.

**Triệu chứng:**
- Người dùng phàn nàn chatbot chậm
- Metrics `/metrics` hiện `latency_p95` > 5000

**Nguyên nhân thường gặp:**
- RAG (tìm kiếm tài liệu) bị chậm → xem traces trong Langfuse
- Server bị overload → kiểm tra CPU/Memory
- Incident đang được inject (giả lập) → gọi `/incidents/rag_slow/disable`

**Cách xử lý:**
1. Mở Langfuse → xem trace nào có span chậm nhất
2. Đọc log: `cat data/logs.jsonl | grep "rag"` → tìm dòng có latency cao
3. Nếu là RAG: `python scripts/inject_incident.py --scenario rag_slow --disable`
4. Nếu là server overload: giảm concurrency hoặc restart server

**Escalation:** Nếu sau 15 phút chưa giải quyết → báo Tech Lead (Trung)

---

## 2. HIGH ERROR RATE

**Mô tả:** Tỷ lệ lỗi vượt 5% trong 5 phút.

**Triệu chứng:**
- Nhiều response trả về HTTP 500
- Metrics `/metrics` hiện `error_breakdown` có giá trị lớn

**Nguyên nhân thường gặp:**
- API key hết hạn hoặc sai cấu hình `.env`
- Import lỗi do dependency thiếu
- Incident `llm_timeout` đang bật

**Cách xử lý:**
1. Xem log gần nhất: `cat data/logs.jsonl | tail -20`
2. Tìm dòng level `error` → đọc `error_type` và `detail`
3. Nếu liên quan LLM timeout: `python scripts/inject_incident.py --scenario llm_timeout --disable`
4. Nếu là config: kiểm tra file `.env`

**Escalation:** Alert này là P1 → báo ngay Tech Lead nếu không rõ nguyên nhân

---

## 3. COST BUDGET SPIKE

**Mô tả:** Chi phí API tăng gấp đôi mức bình thường trong 15 phút.

**Triệu chứng:**
- Metrics `total_cost_usd` tăng nhanh
- `avg_cost_usd` cao bất thường

**Nguyên nhân thường gặp:**
- Load test đang chạy quá nhiều request
- Prompt quá dài (nhiều token_in)
- Vòng lặp lỗi gây gửi request liên tục

**Cách xử lý:**
1. Dừng load test nếu đang chạy (Ctrl+C trong terminal load test)
2. Xem `/metrics` → kiểm tra `tokens_in_total` so với baseline
3. Giảm tần suất request

**Escalation:** Báo FinOps owner nếu chi phí vượt budget ngày

---

## 4. LOW QUALITY SCORE

**Mô tả:** Điểm chất lượng câu trả lời trung bình dưới 0.6 trong 30 phút.

**Triệu chứng:**
- Metrics `quality_avg` < 0.6
- Người dùng phàn nàn câu trả lời không liên quan

**Nguyên nhân thường gặp:**
- RAG không tìm được tài liệu phù hợp (docs rỗng)
- Câu hỏi của user quá ngắn, LLM không hiểu context
- Mock RAG trả về kết quả không liên quan

**Cách xử lý:**
1. Xem traces Langfuse → field `doc_count` trong metadata của observation
2. Nếu `doc_count = 0`: vấn đề với RAG retrieval
3. Xem `query_preview` trong traces → câu hỏi có hợp lệ không

**Escalation:** Báo thành viên phụ trách RAG (Đạt hoặc Trung) để điều tra
```

**Lưu file** (Ctrl+S).

---

### ✅ Bước 4 — Kiểm tra lại (tự kiểm tra trước khi push)

Mở lại 2 file vừa sửa và kiểm tra:

- [ ] `config/alert_rules.yaml`: Có đúng 4 alert rules không?
- [ ] `config/alert_rules.yaml`: Mỗi rule có đủ `name`, `severity`, `description`, `condition`, `owner`, `runbook` không?
- [ ] `docs/alerts.md`: Có đủ 4 mục (High Latency, High Error Rate, Cost Spike, Low Quality) không?
- [ ] Mỗi mục trong `docs/alerts.md`: Có phần "Cách xử lý" và "Escalation" không?

---

### ✅ Bước 5 — Commit và push lên GitHub

```bash
# Lệnh này thêm 2 file vào "danh sách chờ commit"
git add config/alert_rules.yaml docs/alerts.md

# Lệnh này lưu thay đổi với thông điệp mô tả
git commit -m "feat(alerts): thêm alert rule low_quality_score và viết runbook đầy đủ 4 alerts"

# Lệnh này đẩy nhánh lên GitHub
git push origin feature/alerts-nghia
```

> ✅ Sau khi push thành công, **báo Trung** để review và merge vào `main`.

---

## ✅ CHECKLIST HOÀN THÀNH

Tự kiểm tra trước khi báo Trung:

- [ ] Đã tạo nhánh `feature/alerts-nghia`
- [ ] `config/alert_rules.yaml` có 4 alert rules với đầy đủ trường
- [ ] Alert thứ 4 tên `low_quality_score` do Nghĩa tự thêm
- [ ] `docs/alerts.md` có runbook cho cả 4 alerts
- [ ] Mỗi runbook có phần Mô tả, Triệu chứng, Nguyên nhân, Cách xử lý, Escalation
- [ ] Đã commit với message rõ ràng
- [ ] Đã push lên GitHub
- [ ] Đã nhắn Trung để merge
