# 🎯 Attack Scenario - Quick Start Guide

**Mục đích**: Tạo scenarios tấn công/stress test cho hệ thống  
**Thời gian học**: 5 phút  
**Cách sử dụng**: Copy struct dưới đây, thêm scenarios vào file JSON, chạy test

---

## 📝 Schema Đơn Giản

Mỗi scenario có cấu trúc này:

```json
{
  "id": "category_number_name",                 // VD: input_1_missing_field
  "category": "input_validation",               // Loại test
  "name": "Test Name",                         // Tên mô tả
  "description": "Chi tiết test",            // Mô tả 1-2 dòng
  "endpoint": "/chat",                       // API endpoint
  "method": "POST",                         // GET/POST/PUT/DELETE
  "payload": {"content": "", "user_id": ""}, // Request body
  "timeout_seconds": 20,                    // Timeout limit
  "expected_status": 200,                   // Expected HTTP status
  "severity": "high"                        // critical/high/medium/low
}
```

---

## 🎓 Loại Test (Category)

| Category | Ý nghĩa | Ví dụ |
|----------|---------|-------|
| **input_validation** | Test kiểm tra input | Missing field, empty string, invalid format |
| **pii** | Test bảo mật (scrubbing) | Email, phone, CCCD trong message |
| **performance** | Test tốc độ, timeout | Long query, deep processing |
| **concurrency** | Test load đồng thời | 20 requests cùng lúc |
| **error** | Test error handling | 404, 422, 500 |
| **edge_case** | Test trường hợp đặc biệt | Minimum input, special chars |
| **rag** | Test RAG retrieval | Query need knowledge base |

---

## 📋 Ví dụ Scenarios (Dùng Ngay)

### 1. Missing Field Test
```json
{
  "id": "input_1_missing_content",
  "category": "input_validation",
  "name": "Missing Content Field",
  "description": "POST request without content field - should return 422",
  "endpoint": "/chat",
  "method": "POST",
  "payload": {"user_id": "test_user"},
  "timeout_seconds": 5,
  "expected_status": 422,
  "severity": "high"
}
```

### 2. Empty Content Test
```json
{
  "id": "input_2_empty_content",
  "category": "input_validation",
  "name": "Empty Content",
  "description": "Empty string content - should return 422",
  "endpoint": "/chat",
  "method": "POST",
  "payload": {"content": "", "user_id": "test_user"},
  "timeout_seconds": 5,
  "expected_status": 422,
  "severity": "high"
}
```

### 3. PII Email Test
```json
{
  "id": "pii_1_email",
  "category": "pii",
  "name": "Email Scrubbing",
  "description": "Email in content - should scrub in logs but return 200",
  "endpoint": "/chat",
  "method": "POST",
  "payload": {
    "content": "My email is john@example.com, help me with C",
    "user_id": "test_user"
  },
  "timeout_seconds": 20,
  "expected_status": 200,
  "severity": "critical"
}
```

### 4. PII Phone Test
```json
{
  "id": "pii_2_phone",
  "category": "pii",
  "name": "Phone Scrubbing",
  "description": "Vietnam phone number - should scrub in logs",
  "endpoint": "/chat",
  "method": "POST",
  "payload": {
    "content": "Tôi là Nguyễn A, SĐT 0987654321, cần học C",
    "user_id": "test_user"
  },
  "timeout_seconds": 20,
  "expected_status": 200,
  "severity": "critical"
}
```

### 5. PII CCCD Test
```json
{
  "id": "pii_3_cccd",
  "category": "pii",
  "name": "CCCD Scrubbing",
  "description": "ID number - should scrub in logs",
  "endpoint": "/chat",
  "method": "POST",
  "payload": {
    "content": "Số CCCD 123456789012, cần hỗ trợ",
    "user_id": "test_user"
  },
  "timeout_seconds": 20,
  "expected_status": 200,
  "severity": "critical"
}
```

### 6. Long Query Test
```json
{
  "id": "perf_1_long_query",
  "category": "performance",
  "name": "Long Query",
  "description": "3000+ char query - test timeout limits",
  "endpoint": "/chat",
  "method": "POST",
  "payload": {
    "content": "Giải thích chi tiết binary tree implementation trong C bao gồm: 1) Node structure, 2) Insert với balancing, 3) Delete xử lý 3 cases, 4) In-order/Pre-order/Post-order traversal, 5) Level-order traversal, 6) Search function, 7) Height calculation, 8) Serialize/Deserialize. Code 100+ lines với comments, error handling, memory management. Ước tính performance?",
    "user_id": "perf_user"
  },
  "timeout_seconds": 25,
  "expected_status": 200,
  "severity": "high"
}
```

### 7. Invalid Endpoint Test
```json
{
  "id": "error_1_404",
  "category": "error",
  "name": "Invalid Endpoint",
  "description": "Non-existent endpoint - should return 404",
  "endpoint": "/invalid/xyz",
  "method": "POST",
  "payload": {"content": "test", "user_id": "test"},
  "timeout_seconds": 5,
  "expected_status": 404,
  "severity": "low"
}
```

### 8. Minimal Input Test
```json
{
  "id": "edge_1_minimal",
  "category": "edge_case",
  "name": "Minimal Input",
  "description": "Shortest valid query - should work",
  "endpoint": "/chat",
  "method": "POST",
  "payload": {"content": "Hi", "user_id": "test"},
  "timeout_seconds": 20,
  "expected_status": 200,
  "severity": "low"
}
```

### 9. RAG Knowledge Test
```json
{
  "id": "rag_1_knowledge",
  "category": "rag",
  "name": "Course Knowledge",
  "description": "Query about course materials - test RAG retrieval",
  "endpoint": "/chat",
  "method": "POST",
  "payload": {
    "content": "Course materials có những ví dụ nào về con trỏ trong C?",
    "user_id": "rag_user"
  },
  "timeout_seconds": 25,
  "expected_status": 200,
  "severity": "high"
}
```

---