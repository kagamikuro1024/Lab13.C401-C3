"""
Xử lý và loại bỏ thông tin cá nhân nhạy cảm (PII) khỏi log và trace.
Tác giả: Vinh (thực hiện bằng nhánh feature/pii-vinh)
"""
from __future__ import annotations

import hashlib
import re

# Từ điển các pattern PII — mỗi entry: tên → biểu thức regex
# Kết quả redact sẽ là [REDACTED_TEN_VIET_HOA]
PII_PATTERNS: dict[str, str] = {
    # Email: ví dụ abc@gmail.com
    "email": r"[\w\.\-]+@[\w\.\-]+\.\w+",
    # Số điện thoại Việt Nam: 0912345678, +84-912-345-678, v.v.
    "phone/tax_id_vn": r"\b(?:\+84|0)[ .-]?\d{3}[ .-]?\d{3}[ .-]?\d{3,4}\b",
    # Số CCCD/CMND 12 chữ số
    "cccd": r"\b0\d{11}\b",
    # Số thẻ tín dụng 16 chữ số (có thể viết liền hoặc phân cách bằng dấu -)
    "credit_card": r"\b\d{4}[- ]?\d{4}[- ]?\d{4}[- ]?\d{4}\b",
    # Hộ chiếu Việt Nam: 1 chữ cái HOA + 7 chữ số (VD: B1234567)
    "passport_vn": r"\b[A-Z]\d{7}\b",
    # Mã số thuế 10 chữ số hoặc 10-3 chữ số
    # "phone/tax_id_vn": r"\b(?!0\d{9}\b)\d{10}(?:-\d{3})?\b",
    # Địa chỉ có từ khóa số nhà + đường/phố
    "address_vn": r"(?:số\s+\d+\s+(?:đường|phố)|(?:đường|phố)\s+[\w\s]+,\s*(?:quận|huyện|phường|xã))",
}


def scrub_text(text: str) -> str:
    """
    Quét và thay thế tất cả PII trong văn bản bằng [REDACTED_TEN_PATTERN].
    Đây là bộ lọc chính để không lộ thông tin nhạy cảm ra log.
    """
    if not isinstance(text, str):
        return text
    safe = text
    for name, pattern in PII_PATTERNS.items():
        safe = re.sub(pattern, f"[REDACTED_{name.upper()}]", safe, flags=re.IGNORECASE)
    return safe

def hash_user_id(user_id: str) -> str:
    """
    Hash user_id bằng SHA-256, chỉ lấy 12 ký tự đầu.
    Mục đích: không lưu user_id thật vào log/trace để bảo vệ quyền riêng tư.
    """
    return hashlib.sha256(user_id.encode("utf-8")).hexdigest()[:12]

def summarize_text(text: str, max_len: int = 80) -> str:
    """
    Tóm tắt văn bản để hiển thị trong log: scrub PII + cắt ngắn tối đa max_len ký tự.
    """
    if not isinstance(text, str):
        return str(text)
    safe = scrub_text(text).strip().replace("\n", " ")
    return safe[:max_len] + ("..." if len(safe) > max_len else "")
