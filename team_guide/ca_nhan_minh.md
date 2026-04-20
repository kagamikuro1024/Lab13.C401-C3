# 📋 KẾ HOẠCH CÁ NHÂN — MINH
## Day 13: Monitoring, Logging & Observability
### Hệ thống: TA_Chatbot (Backend: `app/backend/`)

> **Nhánh Git cần tạo:** `feature/dashboard-minh`  
> **Nhiệm vụ chính:** Dashboard Implementation + Blueprint Report  
> **Thời gian ước tính:** 90 phút

---

## 🎯 Minh làm gì?

Minh chịu trách nhiệm **trực quan hóa dữ liệu** để nhóm có cái nhìn tổng quan khi demo, đồng thời hoàn thiện báo cáo BluePrint cuối cùng.

Nhiệm vụ:
1. Viết script `scripts/dashboard.py` để in dashboard 6 panels ra terminal.
2. Hoàn thiện báo cáo `docs/blueprint-template.md`.
3. Chuẩn bị các câu hỏi/đáp án demo trong `docs/mock-debug-qa.md`.

---

## 📂 Các file cần tạo / chỉnh sửa

| File | Việc cần làm |
|------|-------------|
| `scripts/dashboard.py` | Tạo script kết nối vào `GET /obs-metrics` của backend chatbot |
| `docs/blueprint-template.md` | Điền thông tin nhóm và kết quả tracing/logging |

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

Minh hãy copy đoạn code này vào file mới. Script này sẽ "vẽ" dashboard ngay trong terminal:

```python
"""
Dashboard 6 panels cho TA_Chatbot (Day 13 Lab)
Chạy: python scripts/dashboard.py --once
"""
import requests
import time

BASE_URL = "http://localhost:8000"

def get_data():
    try:
        # Lấy dữ liệu từ endpoint observability mới của chatbot
        r = requests.get(f"{BASE_URL}/obs-metrics")
        return r.json()
    except:
        return None

def print_dashboard(data):
    if not data:
        print("❌ Không kết nối được backend chatbot (Port 8000)")
        return

    print("="*50)
    print("      📊 TA_CHATBOT OBSERVABILITY DASHBOARD")
    print("="*50)
    print(f"1. Traffic: {data['traffic']} reqs")
    print(f"2. Latency P95: {data['latency_p95']} ms")
    print(f"3. Error Rate: {sum(data['error_breakdown'].values())} errors")
    print(f"4. Total Cost: ${data['total_cost_usd']}")
    print(f"5. Tokens: {data['tokens_in_total']} in / {data['tokens_out_total']} out")
    print(f"6. Quality Score: {data['quality_avg']}")
    print("="*50)

if __name__ == "__main__":
    data = get_data()
    print_dashboard(data)
```

---

### ✅ Bước 3 — Điền Blueprint `docs/blueprint-template.md`

Đây là file quan trọng nhất để nộp bài. Minh phối hợp với Trung để lấy:
- **Validate Log Score**: (Vd: 100/100)
- **Total Traces**: (Số lượng traces trên Langfuse)
- **Root Cause**: Giải thích vì sao hệ thống bị chậm/lỗi trong phần Incident.

---

### ✅ Bước 4 — Commit & Push

```bash
git add scripts/dashboard.py docs/blueprint-template.md
git commit -m "feat(dashboard): tạo script dashboard và hoàn thiện báo cáo blueprint"
git push origin feature/dashboard-minh
```

Xong xuôi báo Trung để merge vào `main` nhé!
