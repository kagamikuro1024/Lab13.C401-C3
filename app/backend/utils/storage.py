import os
import json
import glob
from datetime import datetime

DATA_DIR = "app_data"
METRICS_FILE = os.path.join(DATA_DIR, "metrics.json")
CHATS_DIR = os.path.join(DATA_DIR, "chat_histories")

def init_storage():
    """Tạo thư mục/file nếu chưa tồn tại"""
    os.makedirs(CHATS_DIR, exist_ok=True)
    if not os.path.exists(METRICS_FILE):
        with open(METRICS_FILE, "w", encoding="utf-8") as f:
            json.dump({"helpful": 0, "unhelpful": 0, "escalated": 0, "total": 0}, f)

def get_metrics():
    """Đọc dữ liệu metrics"""
    init_storage()
    with open(METRICS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def update_metric(key: str, value: int = 1):
    """Cập nhật một hoặc thay đổi metrics (key: helpful, unhelpful, escalated, total)"""
    metrics = get_metrics()
    if key in metrics:
        metrics[key] += value
    with open(METRICS_FILE, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=4)

def save_chat_session(session_id: str, messages: list):
    """Lưu trữ cuộc hội thoại"""
    init_storage()
    if not messages:
        return
    filepath = os.path.join(CHATS_DIR, f"{session_id}.json")
    
    # Locate first user message for title
    title = "Chat mới"
    for msg in messages:
        if msg.get("role") == "user":
            title = msg.get("content", "")[:30] + "..."
            break

    # If file exists, we want to retain the original creation time or simply override last_updated
    # Actually, override is fine, since it's a living chat.
    chat_data = {
        "session_id": session_id,
        "last_updated": datetime.now().isoformat(),
        "title": title,
        "messages": messages
    }
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(chat_data, f, ensure_ascii=False, indent=2)

def load_chat_session(session_id: str) -> list:
    """Load lại cuộc trò chuyện"""
    filepath = os.path.join(CHATS_DIR, f"{session_id}.json")
    if os.path.exists(filepath):
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data.get("messages", [])
    return []

def list_past_chats():
    """Lấy danh sách các đoạn chat trước đây, sắp xếp theo thời gian mới nhất"""
    init_storage()
    chats = []
    for filepath in glob.glob(os.path.join(CHATS_DIR, "*.json")):
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
                chats.append({
                    "session_id": data.get("session_id", os.path.basename(filepath).replace('.json', '')),
                    "last_updated": data.get("last_updated", ""),
                    "title": data.get("title", "Đoạn chat chưa đặt tên")
                })
        except Exception:
            pass
    # Xếp lịch sử chat từ mới nhất về cũ nhất
    chats.sort(key=lambda x: x["last_updated"], reverse=True)
    return chats
