# 📋 KẾ HOẠCH CÁ NHÂN — VINH
## Day 13: Monitoring, Logging & Observability
### Hệ thống: TA_Chatbot (Backend: `app/backend/`)

> **Nhánh Git cần tạo:** `feature/pii-vinh`  
> **Nhiệm vụ chính:** Tăng cường PII Protection — Thêm patterns & kiểm thử trên backend thật  
> **Thời gian ước tính:** 60 phút

---

## 🎯 Vinh làm gì?

Trong hệ thống chatbot thật, học viên thường vô tình gửi Email, Số điện thoại hoặc Mã số thuế khi hỏi bài. Hệ thống của chúng ta cần **tự động xóa (redact)** các thông tin này khỏi log để đảm bảo an ninh dữ liệu.

Vinh chịu trách nhiệm:
1. **Thêm PII patterns mới** vào module `app/backend/obs/pii.py`.
2. **Viết test cases** trong `tests/test_pii.py` để kiểm tra module này.
3. **Verify** log thực tế sau khi chạy server.

---

## 📂 Các file cần chỉnh sửa/tạo mới

| File | Việc cần làm |
|------|-------------|
| `app/backend/obs/pii.py` | Thêm Passport VN, Địa chỉ VN, Mã số thuế patterns |
| `tests/test_pii.py` | Cập nhật bộ test để trỏ vào backend/obs/pii.py |

---

## 🔢 TỪNG BƯỚC THỰC HIỆN

### ✅ Bước 1 — Tạo nhánh Git

```bash
git checkout main
git pull origin main
git checkout -b feature/pii-vinh
```

---

### ✅ Bước 2 — Mở và chỉnh sửa `app/backend/obs/pii.py`

Mở file `app/backend/obs/pii.py` (Lưu ý: file nằm trong folder backend). 

**Thay toàn bộ nội dung** bằng code sau để đảm bảo có đủ 7 patterns (Vinh đã thêm 3 patterns mới):

```python
"""
Module xử lý PII cho TA_Chatbot backend.
Cập nhật bởi: Vinh (Day 13 Lab)
"""
from __future__ import annotations
import hashlib
import re

PII_PATTERNS: dict[str, str] = {
    "email": r"[\w\.\-]+@[\w\.\-]+\.\w+",
    "phone_vn": r"(?:\+84|0)[ \.\-]?\d{3}[ \.\-]?\d{3}[ \.\-]?\d{3,4}",
    "cccd": r"\b\d{12}\b",
    "credit_card": r"\b\d{4}[- ]?\d{4}[- ]?\d{4}[- ]?\d{4}\b",
    
    # --- Pattern mới của Vinh ---
    "passport_vn": r"\b[A-Z]\d{7}\b",
    "tax_id_vn": r"\b\d{10}(?:-\d{3})?\b",
    "address_vn": r"(?:số\s+\d+\s+(?:đường|phố)|(?:đường|phố)\s+[\w\s]+,\s*(?:quận|huyện|phường|xã))",
}

def scrub_text(text: str) -> str:
    """Quét và thay thế PII bằng [REDACTED_TEN_PATTERN]"""
    if not isinstance(text, str): return text
    safe = text
    for name, pattern in PII_PATTERNS.items():
        safe = re.sub(pattern, f"[REDACTED_{name.upper()}]", safe, flags=re.IGNORECASE)
    return safe

def hash_user_id(user_id: str) -> str:
    """Hash user_id để không lộ danh tính thật trong log"""
    return hashlib.sha256(user_id.encode("utf-8")).hexdigest()[:12]

def summarize_text(text: str, max_len: int = 80) -> str:
    """Scrub PII + Cắt ngắn cho log"""
    if not isinstance(text, str): return str(text)
    safe = scrub_text(text).strip().replace("\n", " ")
    return safe[:max_len] + ("..." if len(safe) > max_len else "")
```

---

### ✅ Bước 3 — Cập nhật `tests/test_pii.py`

Vì chúng ta đã chuyển code vào `app/backend/obs/`, Vinh cần cập nhật đường dẫn import trong file test.

Mở `tests/test_pii.py` (ở thư mục gốc) và thay code:

```python
import sys
from pathlib import Path
# Thêm đường dẫn backend vào sys.path để test có thể import được module obs
sys.path.insert(0, str(Path(__file__).parent.parent / "app" / "backend"))

from obs.pii import scrub_text, hash_user_id

def test_pii_scrubbing():
    # Test Email
    assert "[REDACTED_EMAIL]" in scrub_text("Email: test@example.com")
    # Test Passport (mới)
    assert "[REDACTED_PASSPORT_VN]" in scrub_text("Hộ chiếu B1234567")
    # Test Tax ID (mới)
    assert "[REDACTED_TAX_ID_VN]" in scrub_text("MST: 0123456789")

def test_user_id_hashing():
    uid = "student_001"
    hashed = hash_user_id(uid)
    assert len(hashed) == 12
    assert uid not in hashed
```

---

### ✅ Bước 4 — Chạy thử nghiệm

```bash
# Chạy unit test
python -m pytest tests/test_pii.py -v
```

Sau đó gửi request thật để xem log:
```bash
# Terminal 1: Khởi động server (cd app/backend trước)
python -m uvicorn app.main:app --port 8000

# Terminal 2: Gửi câu hỏi có Email
curl -X POST http://localhost:8000/chat -H "Content-Type: application/json" -d "{\"content\": \"Hỏi về malloc, email em là abc@gmail.com\", \"user_id\": \"vinh-test\"}"

# Kiểm tra log
type data\logs.jsonl | findstr /i "REDACTED"
```

---

### ✅ Bước 5 — Commit & Push

```bash
git add app/backend/obs/pii.py tests/test_pii.py
git commit -m "feat(pii): hoàn thiện 7 PII patterns cho backend chatbot và bộ test"
git push origin feature/pii-vinh
```

Báo cho Trung (Tech Lead) sau khi hoàn thành.
