import requests
import json
import time
from pathlib import Path

BASE_URL = "http://localhost:8000"

SCENARIOS = [
    # 1. Chat thông thường để sinh dữ liệu
    {"id": "1_chat", "name": "Basic Chat", "endpoint": "/chat", "payload": {"content": "Con tro trong C la gi?", "user_id": "u1"}},
    
    # 2. Feedback có kèm nội dung (Admin theo dõi trực tiếp)
    {"id": "2_audit_feedback_good", "name": "Admin Audit: Helpful Feedback", "endpoint": "/feedback", 
     "payload": {
         "type": "helpful", 
         "target_id": "req-123456", 
         "answer_content": "Con trỏ là biến lưu trữ địa chỉ của biến khác. Ví dụ: int *p = &a;"
     }},
     
    {"id": "3_audit_feedback_bad", "name": "Admin Audit: Unhelpful Feedback", "endpoint": "/feedback", 
     "payload": {
         "type": "unhelpful", 
         "target_id": "req-999999", 
         "answer_content": "Tôi không biết con trỏ là gì, hãy hỏi người khác."
     }},

    # 3. Chặn đánh giá trùng lặp
    {"id": "4_audit_duplicate", "name": "Admin Audit: Duplicate Block", "endpoint": "/feedback", 
     "payload": {
         "type": "helpful", 
         "target_id": "req-123456", 
         "answer_content": "Test duplicate"
     }},

    # 4. Các sự kiện hệ thống khác
    {"id": "5_audit_escalate", "name": "Admin Audit: Manual Escalation", "endpoint": "/escalate", 
     "payload": {"content": "Vấn đề kỹ thuật nghiêm trọng", "user_id": "trung"}}
]

def run_scenarios():
    print(f"--- STARTING ADMIN AUDIT MONITORING TEST ---")
    
    for scene in SCENARIOS:
        print(f"\n[Scenario {scene['id']}] Running: {scene['name']}...")
        try:
            r = requests.post(f"{BASE_URL}{scene['endpoint']}", json=scene['payload'], timeout=30)
            print(f"Status: {r.status_code}")
            print(f"Response: {r.text[:100]}")
        except Exception as e:
            print(f"Network Error: {e}")
        
        time.sleep(2) 

    print("\n--- ALL ADMIN SCENARIOS COMPLETED ---")
    print("Moi Trung kiem tra Live Audit Stream de thay AI Answer tracking!")

if __name__ == "__main__":
    run_scenarios()
