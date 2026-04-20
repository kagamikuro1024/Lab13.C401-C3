# 📋 KẾ HOẠCH CÁ NHÂN — VINH
## Day 13: Monitoring, Logging & Observability

> **Nhánh Git cần tạo:** `feature/pii-vinh`  
> **Nhiệm vụ chính:** Tăng cường PII Protection — Thêm patterns & kiểm thử  
> **Thời gian ước tính:** 60–75 phút

---

## 🎯 Vinh làm gì?

**PII** (Personal Identifiable Information) là thông tin cá nhân nhạy cảm như email, số điện thoại, số CCCD. Hệ thống cần **tự động xóa (redact)** các thông tin này khỏi log trước khi ghi.

Vinh chịu trách nhiệm:
1. **Thêm PII patterns** mới vào `app/pii.py` (hiện có 4, cần thêm ít nhất 2 pattern mới)
2. **Viết test case** để kiểm tra chức năng PII scrubbing
3. **Kiểm tra** log thực tế không có PII lọt qua

---

## 📂 Các file cần chỉnh sửa/tạo mới

| File | Việc cần làm |
|------|-------------|
| `app/pii.py` | Thêm Passport VN, địa chỉ VN, Mã số thuế patterns |
| `tests/test_pii.py` | Tạo mới: test cases kiểm tra PII scrubbing |

---

## 🧠 Hiểu nhanh về code

Mở file `app/pii.py`. Bạn sẽ thấy:

```python
PII_PATTERNS: dict[str, str] = {
    "email": r"[\w\.-]+@[\w\.-]+\.\w+",           # Ví dụ: abc@gmail.com → [REDACTED_EMAIL]
    "phone_vn": r"(?:\+84|0)[ \.-]?\d{3}...",      # Ví dụ: 0912345678 → [REDACTED_PHONE_VN]
    "cccd": r"\b\d{12}\b",                          # Ví dụ: 123456789012 → [REDACTED_CCCD]
    "credit_card": r"\b\d{4}[- ]?\d{4}[- ]?...",   # Ví dụ: 4111-1111-1111-1111 → [REDACTED_CREDIT_CARD]
}
```

Hàm `scrub_text(text)` tự động áp dụng tất cả patterns lên văn bản và thay thế bằng `[REDACTED_TEN_PATTERN]`.

---

## 🔢 TỪNG BƯỚC THỰC HIỆN

### ✅ Bước 1 — Tạo nhánh Git

```bash
git checkout main
git pull origin main
git checkout -b feature/pii-vinh
```

---

### ✅ Bước 2 — Thêm PII Patterns vào `app/pii.py`

Mở file `app/pii.py`.

**Thay toàn bộ nội dung** bằng code sau (đã có sẵn 4 patterns cũ + 3 patterns mới do Vinh thêm):

```python
from __future__ import annotations

import hashlib
import re

# Từ điển các pattern PII (thông tin cá nhân nhạy cảm)
# Mỗi pattern: tên → biểu thức chính quy (regex)
# Kết quả redact: [REDACTED_TEN_VIET_HOA]
PII_PATTERNS: dict[str, str] = {
    # Pattern gốc — có sẵn từ template
    "email": r"[\w\.-]+@[\w\.-]+\.\w+",
    # Số điện thoại Việt Nam: 0912 345 678, +84-912-345-678, v.v.
    "phone_vn": r"(?:\+84|0)[ \.-]?\d{3}[ \.-]?\d{3}[ \.-]?\d{3,4}",
    # Số CCCD/CMND mới 12 chữ số
    "cccd": r"\b\d{12}\b",
    # Số thẻ tín dụng 16 chữ số (có thể viết liền hoặc cách bằng dấu -)
    "credit_card": r"\b\d{4}[- ]?\d{4}[- ]?\d{4}[- ]?\d{4}\b",

    # Pattern mới — DO VINH THÊM
    # Hộ chiếu Việt Nam: 1 chữ cái + 7 chữ số (ví dụ: B1234567, C9876543)
    "passport_vn": r"\b[A-Z]\d{7}\b",
    # Mã số thuế cá nhân Việt Nam: 10 chữ số hoặc 10+3 chữ số
    "tax_id_vn": r"\b\d{10}(?:-\d{3})?\b",
    # Địa chỉ Việt Nam: nhận diện khi có từ khóa địa chỉ đặc trưng
    # Ví dụ: "123 Nguyễn Huệ, Quận 1" hoặc "số 45 đường Lê Lợi, phường Bến Nghé"
    "address_vn": r"(?:số\s+\d+\s+(?:đường|phố)|(?:đường|phố)\s+[\w\s]+,\s*(?:quận|huyện|phường|xã))",
}


def scrub_text(text: str) -> str:
    """
    Quét văn bản và thay thế tất cả thông tin PII bằng [REDACTED_TEN_PATTERN].
    Hàm này là lớp bảo vệ chính để không lọ thông tin nhạy cảm ra log.
    """
    safe = text
    for name, pattern in PII_PATTERNS.items():
        safe = re.sub(pattern, f"[REDACTED_{name.upper()}]", safe, flags=re.IGNORECASE)
    return safe


def summarize_text(text: str, max_len: int = 80) -> str:
    """
    Tóm tắt văn bản để hiển thị trong log: scrub PII + cắt ngắn tối đa max_len ký tự.
    """
    safe = scrub_text(text).strip().replace("\n", " ")
    return safe[:max_len] + ("..." if len(safe) > max_len else "")


def hash_user_id(user_id: str) -> str:
    """
    Hash user_id bằng SHA-256, chỉ lấy 12 ký tự đầu.
    Mục đích: không lưu user_id thật vào log/trace, bảo vệ quyền riêng tư.
    """
    return hashlib.sha256(user_id.encode("utf-8")).hexdigest()[:12]
```

**Lưu file.**

---

### ✅ Bước 3 — Tạo file test `tests/test_pii.py`

Kiểm tra xem thư mục `tests/` đã có file nào chưa:
```bash
dir tests\
```

Tạo file mới `tests/test_pii.py` với nội dung sau:

```python
"""
Kiểm thử (unit test) cho module PII scrubbing.
Chạy bằng: python -m pytest tests/test_pii.py -v
"""
from app.pii import scrub_text, hash_user_id, summarize_text


class TestScrubText:
    """Kiểm tra hàm scrub_text()"""

    def test_redact_email(self):
        """Email phải bị xóa"""
        result = scrub_text("Liên hệ qua email trung@example.com nha!")
        assert "[REDACTED_EMAIL]" in result
        assert "@example.com" not in result

    def test_redact_phone_vn(self):
        """Số điện thoại VN phải bị xóa"""
        result = scrub_text("Gọi cho em số 0912345678 nhé")
        assert "[REDACTED_PHONE_VN]" in result
        assert "0912345678" not in result

    def test_redact_phone_with_plus84(self):
        """Số điện thoại dạng +84 cũng phải bị xóa"""
        result = scrub_text("Số của tôi: +84912345678")
        assert "[REDACTED_PHONE_VN]" in result

    def test_redact_cccd(self):
        """Số CCCD 12 chữ số phải bị xóa"""
        result = scrub_text("CCCD của em là 123456789012")
        assert "[REDACTED_CCCD]" in result
        assert "123456789012" not in result

    def test_redact_credit_card(self):
        """Số thẻ tín dụng phải bị xóa"""
        result = scrub_text("Thẻ của tôi: 4111-1111-1111-1111")
        assert "[REDACTED_CREDIT_CARD]" in result

    def test_redact_passport_vn(self):
        """Số hộ chiếu VN phải bị xóa (DO VINH THÊM)"""
        result = scrub_text("Hộ chiếu số B1234567 của tôi")
        assert "[REDACTED_PASSPORT_VN]" in result
        assert "B1234567" not in result

    def test_redact_tax_id(self):
        """Mã số thuế phải bị xóa (DO VINH THÊM)"""
        result = scrub_text("MST của công ty: 0123456789")
        assert "[REDACTED_TAX_ID_VN]" in result

    def test_no_false_positive_normal_text(self):
        """Văn bản bình thường không bị xóa nhầm"""
        result = scrub_text("Hôm nay học về Python rất hay!")
        assert "[REDACTED" not in result
        assert result == "Hôm nay học về Python rất hay!"

    def test_multiple_pii_in_one_text(self):
        """Nhiều loại PII trong 1 văn bản đều bị xóa"""
        text = "Email: abc@gmail.com, SĐT: 0987654321, CCCD: 098765432109"
        result = scrub_text(text)
        assert "[REDACTED_EMAIL]" in result
        assert "[REDACTED_PHONE_VN]" in result
        assert "[REDACTED_CCCD]" in result
        # Không có thông tin thật nào lọt qua
        assert "@gmail.com" not in result
        assert "0987654321" not in result
        assert "098765432109" not in result


class TestHashUserId:
    """Kiểm tra hàm hash_user_id()"""

    def test_hash_is_12_chars(self):
        """Hash phải luôn có đúng 12 ký tự"""
        result = hash_user_id("student-001")
        assert len(result) == 12

    def test_same_input_same_hash(self):
        """Cùng user_id phải cho cùng hash (deterministic)"""
        assert hash_user_id("student-001") == hash_user_id("student-001")

    def test_different_input_different_hash(self):
        """User_id khác nhau phải cho hash khác nhau"""
        assert hash_user_id("student-001") != hash_user_id("student-002")

    def test_original_id_not_recoverable(self):
        """Hash không thể reverse về user_id gốc"""
        hashed = hash_user_id("student-secret-123")
        assert "student-secret-123" not in hashed


class TestSummarizeText:
    """Kiểm tra hàm summarize_text()"""

    def test_truncates_long_text(self):
        """Văn bản dài hơn max_len phải bị cắt ngắn"""
        long_text = "a" * 200
        result = summarize_text(long_text, max_len=80)
        assert len(result) <= 83  # 80 + "..."
        assert result.endswith("...")

    def test_short_text_not_truncated(self):
        """Văn bản ngắn hơn max_len không bị thêm ..."""
        short_text = "Câu hỏi ngắn"
        result = summarize_text(short_text)
        assert not result.endswith("...")

    def test_pii_scrubbed_before_truncate(self):
        """PII phải bị xóa trước khi cắt ngắn"""
        text = "Email: abc@gmail.com " + "x" * 200
        result = summarize_text(text)
        assert "@gmail.com" not in result
        assert "[REDACTED_EMAIL]" in result or len(result) == 83
```

**Lưu file.**

---

### ✅ Bước 4 — Chạy Test để Kiểm Tra

```bash
# Cài pytest nếu chưa có
pip install pytest

# Chạy test (phải đứng ở thư mục gốc Lab13-Observability/)
python -m pytest tests/test_pii.py -v
```

Kết quả mong đợi: **Tất cả tests PASSED** (màu xanh)

Nếu có test FAILED: đọc thông báo lỗi và sửa lại code trong `app/pii.py`.

---

### ✅ Bước 5 — Test Thực Tế qua App

```bash
# Khởi động server (nếu chưa chạy)
uvicorn app.main:app --reload --port 8000

# Gửi request có chứa PII
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d "{\"user_id\": \"test-001\", \"message\": \"Hộ chiếu của tôi là B9876543 và email là test@test.com\", \"feature\": \"qa\", \"session_id\": \"sess-001\"}"

# Kiểm tra log: không được có B9876543 hay test@test.com
cat data/logs.jsonl | findstr /i "B9876543"
# Kết quả mong đợi: không có kết quả nào
```

---

### ✅ Bước 6 — Commit và Push

```bash
git add app/pii.py tests/test_pii.py
git commit -m "feat(pii): thêm passport_vn, tax_id_vn, address_vn patterns; thêm unit tests PII scrubbing"
git push origin feature/pii-vinh
```

**Sau khi push:** báo Trung để merge vào `main`.

---

## ✅ CHECKLIST HOÀN THÀNH

- [ ] Đã tạo nhánh `feature/pii-vinh`
- [ ] `app/pii.py`: Có ≥ 6 PII patterns (4 cũ + ≥ 2 mới của Vinh)
- [ ] `app/pii.py`: Patterns mới có comment giải thích bằng tiếng Việt
- [ ] `tests/test_pii.py`: Tạo mới với ≥ 8 test cases
- [ ] Chạy `pytest tests/test_pii.py -v` → tất cả PASSED
- [ ] Test thực tế: PII không lọt ra trong `data/logs.jsonl`
- [ ] Đã commit với message rõ ràng
- [ ] Đã push lên GitHub và báo Trung
