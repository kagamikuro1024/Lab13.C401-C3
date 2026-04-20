# TA Chatbot Backend

AI Teaching Assistant Backend for C/C++ Course

## Features

- ✅ FastAPI REST API with security layers
- ✅ Rate limiting (20 requests/min per user)
- ✅ Cost tracking & budget protection ($1/user/day)
- ✅ Health monitoring & uptime tracking
- ✅ RAG-based knowledge retrieval
- ✅ Escalation to human TA
- ✅ User feedback collection

## Project Structure

```
backend/
├── app/                      # Application package
│   ├── __init__.py
│   ├── main.py              # FastAPI application entry point
│   ├── config.py            # Configuration constants
│   ├── auth.py              # Authentication & authorization
│   ├── rate_limiter.py      # Sliding window rate limiter
│   ├── cost_guard.py        # Token usage & budget tracking
│   └── health.py            # Health monitoring
│
├── agent.py                 # LangGraph agent with ReAct
├── tools/                   # Custom tools for agent
├── rag/                     # RAG implementation
├── utils/                   # Utility modules
├── knowledge_base/         # Course materials
├── faiss_index/            # Vector store index
│
├── Dockerfile              # Multi-stage Docker build
├── docker-compose.yml      # Full stack (API + Redis + PostgreSQL)
├── render.yaml            # Render.com deployment config
├── requirements.txt       # Python dependencies
├── .env.example           # Environment template
├── .dockerignore          # Docker build ignore
├── .gitignore             # Git ignore
└── README.md             # This file
```

## Setup Instructions

### 1. Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Copy environment file
cp .env.example .env

# Edit .env with your keys
# - OPENAI_API_KEY: Get from https://platform.openai.com/api-keys
# - EMAIL_USER: Your Gmail address
# - EMAIL_PASS: Gmail app password

# Run server
python -m uvicorn app.main:app --reload --port 8000
```

Server: `http://localhost:8000`  
Docs: `http://localhost:8000/docs`

### 2. Docker Build

```bash
docker build -t ta-chatbot-api:latest .
docker run -p 8000:8000 -e OPENAI_API_KEY=sk-proj-xxx ta-chatbot-api:latest
```

### 3. Docker Compose

```bash
cp .env.example .env
docker-compose up -d
```

## API Endpoints

### POST /chat
```json
{
  "content": "Cách cài đặt gcc?",
  "user_id": "student-001"
}
```

Response:
```json
{
  "content": "Bạn có thể tải gcc từ...",
  "cost": 0.0042,
  "remaining_budget": 0.9958,
  "warning": null
}
```

### GET /health
Health check endpoint

### GET /metrics
Application metrics (helpful/unhelpful/escalated counts)

### POST /feedback
```json
{
  "type": "helpful"
}
```

### POST /escalate
Escalate to human TA

## Configuration

Edit `app/config.py`:

```python
MAX_REQUESTS_PER_WINDOW = 20
PER_USER_DAILY_BUDGET = 1.0
GLOBAL_DAILY_BUDGET = 10.0
LLM_MODEL = "gpt-4o"
```

## Deployment

### Render.com
1. Root Directory: `06-lab-complete/backend`
2. Add env vars: `OPENAI_API_KEY`, `EMAIL_USER`, `EMAIL_PASS`
3. Deploy!

### Railway.app
```bash
railway login
railway init
railway up
```

## Troubleshooting

- **Import errors**: Run from backend root: `python -m uvicorn app.main:app`
- **API key not found**: Check `.env` file exists
- **Rate limit too strict**: Adjust `MAX_REQUESTS_PER_WINDOW` in `app/config.py`

## License

MIT © 2026 AI TA
# 📖 TA_Chatbot README — Version 2.0

**Version:** 2.0 (Information Processing Rules)  
**Last Updated:** April 8, 2026  
**Status:** ✅ **Production Ready**

---

## 🎯 Mục Tiêu

TA_Chatbot là một **AI Teaching Assistant** 24/7 cho khóa học **Lập trình C/C++ cơ bản (CS101)**, được thiết kế để:

1. **Giảm 80% khối lượng công việc** cho dàn TA
2. **Giảm thời gian chờ** của học viên từ "giờ" xuống "giây"
3. **Đảm bảo độ tin cậy**: Mọi thông tin từ Knowledge Base, KHÔNG bịa chuyện

---

## ⚡ Quick Start (3 bước)

### Bước 1: Cài Đặt
```bash
pip install -r requirements.txt
echo "OPENAI_API_KEY=sk-..." > .env
python -m rag.indexer  # One-time
```

### Bước 2: Chạy# 🎓 AI Trợ Giảng (Online TA) - Implementation Plan

## Mô tả tổng quan

Xây dựng hệ thống **AI Online TA** hoạt động 24/7 cho khóa học **"Lập trình C/C++ cơ bản"**, sử dụng **OpenAI GPT-4o-mini** với kiến trúc **LangGraph Agent + RAG** và giao diện web **Streamlit**. Hệ thống được trang bị tính năng **Human-in-the-loop (Escalation)**, gửi đánh giá phản hồi từ người học và hệ thống lưu trữ lịch sử tin nhắn.

## Kiến trúc hệ thống

```mermaid
graph TD
    A[👨‍🎓 Học viên] -->|Gửi câu hỏi / Feedback| B[Streamlit Web UI]
    B --> C[LangGraph Agent]
    
    B --> X[(Local Storage: History & Metrics)]
    
    C --> D{Phân luồng câu hỏi}
    
    D -->|Câu hỏi thủ tục/tài liệu| E[🔍 search_course_materials]
    D -->|Lỗi code / debug| F[🐛 analyze_code_error]
    D -->|Thông tin khóa học| G[📋 get_course_info]
    D -->|Quá phức tạp/Bất đồng| H[🚨 escalate_to_human_ta]
    D -->|Không liên quan| I[❌ Từ chối lịch sự]
    
    E --> J[(FAISS Vector Store)]
    J --> K[Knowledge Base]
    K --> K1[📑 Slides bài giảng]
    K --> K2[💻 Code mẫu]
    K --> K3[❓ FAQ]
    K --> K4[📖 Tài liệu tham khảo]
    
    F --> L[GPT-4o-mini Code Analysis]
    G --> M[Course Metadata JSON]
    
    H --> N{Human-in-the-loop Confirmation}
    N -->|Học viên Xác nhận| O[📧 SMTP Email Service to TA]
    N -->|Hủy bỏ| P[Tiếp tục chat]
    
    C -->|Phản hồi| B
    B -->|Hiển thị| A
```

---

## Proposed Changes

### Component 1: Project Foundation

#### requirements.txt
Các dependencies chính (cập nhật mới):
```
langchain>=0.3.0
langchain-openai>=0.2.0
langchain-community>=0.3.0
langgraph>=0.2.0
faiss-cpu>=1.8.0
python-dotenv>=1.0.0
streamlit>=1.40.0
```

#### .gitignore
Ignore thêm folder database cục bộ: `.env`, `__pycache__`, `faiss_index/`, `.venv/`, `app_data/`

---

### Component 2: Knowledge Base (Tài liệu khóa học)

> [!IMPORTANT]
> Đây là phần cốt lõi quyết định chất lượng trả lời. Tài liệu càng phong phú, Agent trả lời càng chính xác.

#### knowledge_base/slides/
Tài liệu bài giảng dạng Markdown, chia theo chủ đề:
- `01_introduction.md` — Giới thiệu C/C++, cài đặt môi trường
- `02_variables_datatypes.md` — Biến, kiểu dữ liệu, nhập xuất
- `03_control_flow.md` — Câu lệnh điều kiện, vòng lặp
- `04_functions.md` — Hàm, tham số, giá trị trả về
- `05_arrays_strings.md` — Mảng, chuỗi ký tự
- `06_pointers.md` — Con trỏ, quản lý bộ nhớ
- `07_structs.md` — Struct, typedef
- `08_file_io.md` — Đọc ghi file

#### knowledge_base/code_samples/
Code mẫu cho từng chủ đề (`.c` files)

#### knowledge_base/faq.md
Các câu hỏi thường gặp (FAQ) với câu trả lời chuẩn

#### knowledge_base/course_info.json
Metadata khóa học: lịch học, link tài liệu, thông tin TA, quy chế,...

---

### Component 3: RAG Pipeline (Vector Store)

#### rag/indexer.py
Script nạp tài liệu vào FAISS vector store
- Dùng `RecursiveCharacterTextSplitter` hoặc `MarkdownHeaderTextSplitter` để chia nhỏ tài liệu
- Embed bằng `OpenAIEmbeddings`
- Lưu FAISS index vào thư mục `faiss_index/` để tái sử dụng
- Có metadata tracking (nguồn tài liệu, chương, loại) để filter khi search

#### rag/retriever.py
Module load FAISS index và thực hiện similarity search
- `load_vector_store()` — Load index đã lưu
- `search_documents(query, k=5)` — Tìm tài liệu liên quan nhất

---

### Component 4: Agent Tools

#### tools/search_materials.py — `search_course_materials`
- **Input**: Câu hỏi của học viên
- **Logic**: Dùng RAG retriever tìm trong knowledge base (slides, code mẫu, FAQ)
- **Output**: Trích dẫn tài liệu liên quan kèm source attribution

#### tools/code_analyzer.py — `analyze_code_error`
- **Input**: Đoạn code C/C++ bị lỗi + mô tả lỗi
- **Logic**: Phân tích syntax/logic error, đề xuất fix. Sử dụng context từ knowledge base
- **Output**: Giải thích lỗi + gợi ý sửa + giải thích kiến thức liên quan

#### tools/course_info.py — `get_course_info`
- **Input**: Loại thông tin cần tra cứu (lịch học, link tài liệu, TA info,...)
- **Logic**: Tra cứu file `course_info.json`
- **Output**: Thông tin khóa học được format đẹp

#### tools/escalation.py — `escalate_to_human_ta`
- **Input**: student_question, summary, reason, attempted_solutions
- **Logic**: Kích hoạt ngay lập tức khi phát hiện sự phức tạp vượt mức, lỗi từ phía nền tảng, hoặc khi người học bất đồng quan điểm, mong muốn báo cáo dispute. Sinh ra Escalation Report một cách cấu trúc.
- **Output**: Generates report giúp Streamlit App kích hoạt tính năng Xác nhận ở Frontend.

---

### Component 5: Utilities (Lưu trữ và Gửi Email)

#### utils/email_service.py
- **Chức năng**: Gửi email thông báo cho TA phụ trách (ví dụ: `26ai.trunglvq@vinuni.edu.vn`) thông qua thư viện `smtplib` khi học viên chốt yêu cầu Escalation.
- **Bảo mật**: Lấy thông số SMTP server, `EMAIL_USER` và `EMAIL_PASS` tự động từ quá trình cấu hình `.env`.

#### utils/storage.py
- **Chức năng**:
  - Lưu và tracking Metrics (Số lần được dùng AI, số đánh giá Hữu ích 👍, Không hữu ích 👎, Số lượt leo thang ⚠️) bằng json tại `app_data/metrics.json`.
  - Quản lý phiên Session của User. Lưu lại lịch sử hội thoại dưới dạng JSON lưu từng file ở `app_data/chat_histories/` qua hàm `save_chat_session()` và `load_chat_session()`.

---

### Component 6: LangGraph Agent

#### agent.py
Agent chính với kiến trúc LangGraph.

**System Prompt chi tiết** bao gồm:
1. **Vai trò**: TA AI thân thiện, kiên nhẫn, luôn khuyến khích học viên
2. **Phân luồng**: Call chuẩn các Tools tương ứng bao gồm Escalation.
3. **Nguyên tắc sư phạm**: Không nhồi nhét code có sẵn mà phải hướng dẫn step-by-step.
4. **Giới hạn**: Chỉ trả lời liên quan C/C++. Khi người học từ chối cách giải hay yêu cầu gặp người thật, tự động dùng tool `escalate_to_human_ta` không kỳ kèo.

---

### Component 7: Streamlit Web UI

#### app.py
Giao diện chat tích hợp sâu các tiện ích mở rộng:
- **Chat Interface**: Stream text từ AI. Có các nút 👍 👎 ngay dưới từng tin nhắn trả lời để người học đánh giá (cập nhật thông qua `storage.py`).
- **Human-in-the-Loop Confirmation**: Tính năng chặn AI tự ý đưa thông tin leo thang cho người thật. Giao diện sẽ hiển thị nút ✅ Xác nhận (gọi `send_escalation_email`) hoặc ❌ Hủy bỏ cho người học tự quyết định.
- **Sidebar thông minh**:
  - Dashboard thống kê AI (Metrics).
  - Component Khôi phục Chat trước đó (sắp xếp từ mới nhất) nằm ở panel bên trái.
  - Phím tắt Start Chat Session mới (`uuid`).
  - Dark mode / Light mode toggle.
  - Cung cấp quick action questions cho người học thao tác nhanh.

---

## Cấu trúc thư mục hoàn chỉnh

```
TA_Chatbot/
├── .env                        # API keys (OPENAI_API_KEY, EMAIL_USER, EMAIL_PASS)
├── .gitignore
├── requirements.txt
├── app.py                      # Streamlit Web UI (entry point)
├── agent.py                    # LangGraph Agent definition
├── config.py                   # Configuration constants
├── app_data/                   # Nơi chứa DB Local
│   ├── metrics.json            # Biểu đồ đánh giá
│   └── chat_histories/         # Các file JSON lịch sử phiên hội thoại
├── tools/
│   ├── __init__.py
│   ├── search_materials.py     # RAG search tool
│   ├── code_analyzer.py        # Code analysis tool
│   ├── course_info.py          # Course info lookup
│   └── escalation.py           # Escalation logic sinh report
├── rag/
│   ├── __init__.py
│   ├── indexer.py              # Build FAISS index
│   └── retriever.py            # Load & query index
├── utils/
│   ├── __init__.py
│   ├── email_service.py        # Module gửi email tự động dạng SMTP
│   └── storage.py              # Logic đọc/ghi file local json
├── knowledge_base/
│   ├── slides/                 # Tài liệu bài giảng (.md)
│   ├── code_samples/           # Code mẫu (.c)
│   ├── faq.md
│   └── course_info.json
└── faiss_index/                # Generated FAISS index (gitignored)
```

---

## Verification Plan

### Automated / Functional Tests
1. Chạy `python rag/indexer.py` — build FAISS index thành công.
2. Kiểm tra log của file `app_data/metrics.json` có tự động cộng số lượng khi bấm 👍, 👎 hay không.
3. Kích hoạt `escalate_to_human_ta`, chắc chắn UI bị ngắt hiển thị input chat và xuất hiện form Xác nhận gửi email. 

### Manual Verification (Test Scenarios)
| # | Kịch bản test | Kỳ vọng |
|---|---|---|
| 1 | "Em không hiểu, giải thích lại được không?" (Nhiều lần hoặc cố tình bắt bẻ) | → AI escalation ngay lập tức thay vì spam hướng dẫn cũ. |
| 2 | "Đợi tí em muốn hỏi TA người thật." | → Generate Escalation Report -> Streamlit UI chờ bấm Xác nhận gửi. |
| 3 | Bấm nút "✅ Xác nhận Gửi TA" thay vì Hủy bỏ | → Hiện spinner đang gửi. Hoàn thành thì check email gốc cấu hình xem có thư báo tới TA hay không, record metrics "escalated" +1. |
| 4 | Reload trang Streamlit | → Toàn bộ Lịch sử hiển thị trên Sidebar có thể được load lại, context không bị rớt. |
| 5 | "Cách nấu phở bò?" | → AI Từ chối lịch sự, tránh gọi tool. |

```bash
streamlit run app.py
```

### Bước 3: Test
```bash
python test_new_rules.py
```

---

## 📋 Quy Tắc Xử Lý Thông Tin (3 Rules)

### **Rule 1: Phân Loại Chính Xác**
- Weekly Assignments ≠ Labs ≠ Projects
- Mỗi loại có deadline policy khác nhau
- AI phải xác định chính xác trước khi trả lời

### **Rule 2: Trích Xuất & Grounding**
- Mọi info từ Knowledge Base
- Ghi rõ nguồn: "(Theo course_info.json)"
- KHÔNG tự bịa ngày tháng

### **Rule 3: Xử Lý Thông Tin Thiếu**
- Nếu không có → Escalate cho TA
- Nếu "nằm ở LMS" → Báo & hỏi có cần tag TA

---

## 🚀 Escalation System (3 Trigger Levels)

| Trigger | Condition | Action |
|---------|-----------|--------|
| **Trigger 1** | Sinh viên yêu cầu ("Hỏi TA") | Escalate ngay |
| **Trigger 2** | Thông tin không tìm được | Escalate tự động |
| **Trigger 3** | Sinh viên phản bác lần 2+ | Escalate |

---

## 🧪 Test Results

```
✅ TEST 1: Technical Question (Con trỏ?) → PASS
✅ TEST 2: Deadline Question (Project 1?) → PASS
✅ TEST 3: Grading Info (Cách tính điểm?) → PASS
✅ TEST 4: TRIGGER 1 (Hỏi TA giúp) → PASS
```

---

## 📚 Documentation

| File | Purpose |
|------|---------|
| [UPDATE_SUMMARY.md](UPDATE_SUMMARY.md) | Tóm tắt update chi tiết |
| [INFORMATION_PROCESSING_RULES.md](INFORMATION_PROCESSING_RULES.md) | Quy tắc xử lý thông tin |
| [DEVELOPER_GUIDE.md](DEVELOPER_GUIDE.md) | Hướng dẫn phát triển |
| [DEBUG_REPORT.md](DEBUG_REPORT.md) | Các lỗi đã sửa |

---

## 💬 Example Conversations

### Con trỏ là gì?
```
👤: "Con trỏ là gì?"
🎓: "Con trỏ là biến lưu trữ địa chỉ...
     (Theo slide Chương 6 - Pointers)
     Bạn có cần giải thích thêm không?"
```

### Project 1 deadline?
```
👤: "Project 1 deadline khi nào?"
🎓: "Project 1 deadline: 30/03/2026
     (Theo course_info.json)
     Trễ sẽ trừ 10%/ngày, tối đa 5 ngày."
```

### Hỏi TA
```
👤: "Hỏi TA giúp em with"
🎓: "Đã chuyên cho TA. Sẽ phản hồi sớm. 📞"
[ESCALATED]
```

---

## 🔧 Tech Stack

- **Framework**: LangChain + LangGraph
- **LLM**: OpenAI GPT-4o-mini
- **RAG**: FAISS
- **Frontend**: Streamlit
- **Language**: Python 3.9+

---

## 📞 Support

**Need help?**
- Check [INFORMATION_PROCESSING_RULES.md](INFORMATION_PROCESSING_RULES.md)
- See examples in [test_new_rules.py](test_new_rules.py)
- Read [DEVELOPER_GUIDE.md](DEVELOPER_GUIDE.md)

---

**✅ Ready for production deployment!** 🚀
