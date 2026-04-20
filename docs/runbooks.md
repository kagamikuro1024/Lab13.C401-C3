# 📘 TA Chatbot | Incident Response Runbooks

Tài liệu này hướng dẫn cách xử lý các sự cố được phát hiện bởi hệ thống giám sát Observability Pro.

---

## 🔴 [HighLatency] Độ trễ hệ thống cao
**Mô tả:** P90 Latency vượt quá ngưỡng 2000ms.

### Các bước xử lý:
1.  **Kiểm tra LLM:** Xác định xem OpenAI API có đang chậm không (Check status.openai.com).
2.  **Kiểm tra RAG:** Kiểm tra kích thước file Index FAISS. Nếu quá lớn, hãy cân nhắc tối ưu hóa việc phân mảnh (chunking).
3.  **Tối ưu hóa Code:** Kiểm tra xem có vòng lặp vô hạn hoặc xử lý đồng bộ (blocking) trong `agent.py` không.

---

## 🟡 [BudgetWarning] Cảnh báo ngân sách
**Mô tả:** Chi phí tích lũy đạt trên 80% hạn mức ($8.00 / $10.00).

### Các bước xử lý:
1.  **Xác định User:** Sử dụng Dashboard để tìm UserID đang tiêu tốn nhiều token nhất.
2.  **Điều chỉnh Quote:** Giảm `PER_USER_DAILY_BUDGET` trong file `.env`.
3.  **Kiểm tra Prompt:** Xem xét các câu hỏi quá dài (Stress Test Scenario 2) và tối ưu hóa System Prompt để ngắn gọn hơn.

---

## 🔴 [CriticalError] Lỗi hệ thống nghiêm trọng
**Mô tả:** Phát hiện lỗi 500 hoặc ngoại lệ không xác định (Exception).

### Các bước xử lý:
1.  **Sử dụng Drill-down:** Click vào Transaction bị lỗi trên Dashboard để xem `Raw JSON` nhằm xác định lỗi cụ thể (Type Error, File Not Found, etc.).
2.  **Restart Dịch vụ:** Thực hiện khởi động lại Uvicorn server.
3.  **Kiểm tra Audit Logs:** Xem file `data/audit.jsonl` để biết bối cảnh xảy ra lỗi.

---

*Tài liệu được tạo tự động bởi hệ thống Observability Pro v2.4*
