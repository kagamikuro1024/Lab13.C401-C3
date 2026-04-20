# 📋 KẾ HOẠCH CÁ NHÂN — ĐẠT
## Day 13: Monitoring, Logging & Observability
### Hệ thống: TA_Chatbot (Backend: `app/backend/`)

> **Nhánh Git cần tạo:** `feature/slo-dat`  
> **Nhiệm vụ chính:** SLO Configuration + Bằng chứng chấm điểm (Evidence)  
> **Thời gian ước tính:** 50 phút

---

## 🎯 Đạt làm gì?

Đạt chịu trách nhiệm định nghĩa "thế nào là chạy tốt" cho chatbot và thu thập bằng chứng để lấy điểm Rubric cao nhất.

Nhiệm vụ:
1. Thiết lập các cam kết chất lượng (SLO) trong `config/slo.yaml`.
2. Hoàn thiện bảng bằng chứng trong `docs/grading-evidence.md`.
3. Chạy lệnh validate để kiểm tra độ "sạch" của log.

---

## 📂 Các file cần chỉnh sửa

| File | Việc cần làm |
|------|-------------|
| `config/slo.yaml` | Định nghĩa Latency (<3s), Error (<2%), chi phí ($), quality (>0.75) |
| `docs/grading-evidence.md` | Điền các đường dẫn commit và kết quả đo lường thực tế |

---

## 🔢 TỪNG BƯỚC THỰC HIỆN

### ✅ Bước 1 — Tạo nhánh Git

```bash
git checkout main
git pull origin main
git checkout -b feature/slo-dat
```

---

### ✅ Bước 2 — Cập nhật SLO vào `config/slo.yaml`

Định nghĩa các chỉ số thật cho TA_Chatbot:

```yaml
service: ta-chatbot-backend
window: 28d

slis:
  latency_p95_ms:
    objective: 5000       # Chatbot được phép phản hồi trong 5s (vì có LLM)
    target: 99.0
  error_rate_pct:
    objective: 2
    target: 99.9
  daily_cost_usd:
    objective: 5.0
    target: 100.0
  quality_score_avg:
    objective: 0.7
    target: 95.0

evidence:
  measured_latency_p95_ms: "" # Chạy load test xong điền vào đây
  validate_logs_score: ""     # Chạy python scripts/validate_logs.py rồi điền
```

---

### ✅ Bước 3 — Thu thập bằng chứng (Evidence)

Chạy validator:
```bash
python scripts/validate_logs.py
```

Điền kết quả vào `docs/grading-evidence.md`. Lưu ý điền đúng score (vd: 100/100).

---

### ✅ Bước 4 — Sinh dữ liệu test bằng Frontend

> 💡 **Cách dễ nhất:** Dùng giao diện chat thay vì gõ lệnh!

1. Mở terminal → khởi động frontend:
   ```bash
   cd app/frontend
   npm run dev
   ```
2. Mở trình duyệt → `http://localhost:3000`
3. **Chat thử 5–10 câu hỏi** (ví dụ: *"Con trỏ là gì?"*, *"Vòng lặp for trong C"*)
4. Quay lại terminal backend → thấy log JSON nhảy lên là thành công!

Sau đó kiểm tra metrics thật:
```bash
curl http://localhost:8000/obs-metrics
```
Đạt hãy đảm bảo các chỉ số `latency_p50`, `latency_p95` trả về đúng định dạng số.

---

### ✅ Bước 5 — Commit & Push

```bash
git add config/slo.yaml docs/grading-evidence.md
git commit -m "docs(slo): hoàn thiện SLO targets và bằng chứng chấm điểm cho chatbot"
git push origin feature/slo-dat
```
