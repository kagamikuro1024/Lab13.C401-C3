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
