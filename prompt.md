# DAY 13 LAB: MONITORING, LOGGING & OBSERVABILITY

---

## 📌 BỐI CẢNH

Tôi (**Trung**) là **Tech Lead** của nhóm 5 người, đang thực hiện bài lab **Day 13 — Monitoring, Logging & Observability** (template repo, thời lượng 4 giờ hands-on).

Hệ thống nền tảng của nhóm là **TA_Chatbot**, đã được tích hợp sẵn vào:

- `app/frontend/` — giao diện chatbot
- `app/backend/` — backend xử lý

Toàn bộ yêu cầu của bài lab sẽ được **triển khai trên hệ thống TA_Chatbot này**, không phải trên app mẫu của template.

---

## 👥 THÀNH VIÊN & VAI TRÒ

| Thành viên | Vai trò | Ghi chú |
|---|---|---|
| **Trung** (tôi) | Tech Lead | Cầm repo, merge nhánh feature → main, thực hiện end-to-end |
| **Nghĩa** | Member | Nền tảng yếu — chỉ giao task đơn giản, có hướng dẫn rõ ràng từng bước |
| **Đạt** | Member | Nền tảng trung bình — có thể đảm nhận task kỹ thuật vừa |
| **Vinh** | Member | Nền tảng trung bình — có thể đảm nhận task kỹ thuật vừa |
| **Minh** | Member | Nền tảng trung bình — có thể đảm nhận task kỹ thuật vừa |

---

## 🎯 NHIỆM VỤ CỦA TRUNG (TECH LEAD)

Trung sẽ trực tiếp thực hiện và chịu trách nhiệm các phần sau trên nhánh `main`:

- Structured logging & PII masking
- Distributed tracing & tags
- Load testing
- Incident injection
- Blueprint architecture
- Demo lead (chạy demo local trước, sau đó lên cloud nếu cần)
- Merge tất cả nhánh feature của thành viên vào `main`

---

## 📥 ĐẦU VÀO

1. Toàn bộ file hướng dẫn bài lab Day 13 (README, checklist, rubric, v.v.)
2. Source code hệ thống TA_Chatbot tại `app/frontend/` và `app/backend/`
3. Template báo cáo cá nhân và báo cáo nhóm (nếu có trong repo)

> **⚠️ Yêu cầu Agent:** Đọc toàn bộ tài liệu và source code **trước khi bắt đầu bất kỳ bước nào**. Xác định rõ cấu trúc dự án. Các file template mẫu không còn cần thiết (do đã có hệ thống TA_Chatbot thay thế) thì **xóa luôn** để repo gọn gàng.

---

## 📤 ĐẦU RA YÊU CẦU

Agent cần tạo ra **6 file tài liệu** sau:

---

### 1. `end_to_end_script.md` — Kịch bản tổng thể cho Tech Lead (Trung)

Bao gồm:

- Toàn bộ các bước từ setup → hoàn thiện lab theo đúng trình tự
- Tại mỗi bước: mô tả rõ Trung làm gì, merge nhánh nào, kiểm tra gì
- Ghi rõ **điểm dừng (checkpoint)** sau mỗi bước quan trọng → Trung phải xác nhận trước khi tiếp tục
- Sơ đồ luồng nhánh Git (ai tạo nhánh gì, merge vào đâu, khi nào)
- Hướng dẫn chạy **demo local** đầy đủ (bước đầu tiên, trước khi làm bất cứ thứ gì khác)

---

### 2–5. `ca_nhan_[ten].md` — Kế hoạch cá nhân cho từng thành viên

Tạo **4 file riêng biệt**:

- `ca_nhan_nghia.md`
- `ca_nhan_dat.md`
- `ca_nhan_vinh.md`
- `ca_nhan_minh.md`

Mỗi file phải ghi rõ:

- **Nhiệm vụ cụ thể** của thành viên đó trong bài lab
- **Tên nhánh Git** cần tạo (ví dụ: `feature/logging-nghia`)
- **Từng bước thực hiện**: làm gì → file nào → commit message cụ thể
- **Checklist hoàn thành** để tự kiểm tra trước khi push lên nhánh

> 📝 **Lưu ý riêng với file của Nghĩa:** Task phải đơn giản, giải thích từng dòng lệnh, không yêu cầu hiểu sâu kiến trúc hệ thống.

---

### 6. `ke_hoach_lab.md` — Kế hoạch thực hiện lab cho Trung (chạy độc lập)

Kế hoạch này cho phép Trung **tự làm toàn bộ lab trên máy mình** mà **không cần chờ thành viên** commit, bao gồm:

- Danh sách bước theo thứ tự ưu tiên, có thời gian ước tính
- Sau **mỗi bước**: ghi rõ lệnh `git commit` cần thực hiện
- Sau mỗi bước quan trọng: ghi rõ dòng sau để dừng lại chờ xác nhận:

  ```
  ⏸️ [DỪNG LẠI — Trung kiểm tra kết quả trước khi tiếp tục]
  ```

- Đủ chi tiết để **Agent khác có thể thực thi từng bước ngay lập tức** mà không bị xung đột

---

## ⚙️ QUY ƯỚC BẮT BUỘC

| # | Quy ước |
|---|---|
| 1 | Toàn bộ **comment trong code, docstring, và nội dung tài liệu** phải viết bằng **Tiếng Việt**, rõ ràng, dễ hiểu |
| 2 | Mọi file template không còn cần thiết sau khi tích hợp TA_Chatbot → **xóa khỏi repo** |
| 3 | Git workflow: mỗi thành viên làm trên nhánh `feature/<ten-task>-<ten-nguoi>`, Trung review và merge vào `main` |
| 4 | Ưu tiên **chạy demo local** trước khi làm bất kỳ tác vụ observability nào |
| 5 | Mọi output của Agent phải đủ chi tiết để thực thi ngay, không cần hỏi thêm |

---

## ❓ CÂU HỎI AGENT CẦN LÀM RÕ TRƯỚC KHI BẮT ĐẦU

Nếu Agent cần làm rõ thêm, hãy liệt kê các câu hỏi theo thứ tự ưu tiên **trước khi xuất bất kỳ output nào**. Ví dụ gợi ý:

1. Repo đã có `docker-compose.yml` chưa? Hay cần tạo mới cho TA_Chatbot?
2. Stack observability ưu tiên dùng gì? (Prometheus + Grafana? ELK? OpenTelemetry?)
3. Bài lab có yêu cầu deploy lên cloud không, hay chỉ local?
4. Có file rubric/checklist chấm điểm cụ thể không? (để đảm bảo đủ điểm cho từng thành viên)

---

## 🚦 LƯU Ý CUỐI — QUAN TRỌNG

> ❌ **Chưa thực hiện bất kỳ bước nào** cho đến khi Trung xác nhận bằng lệnh **"Bắt đầu đi"**.
>
> ✅ Hãy bắt đầu bằng việc **đọc toàn bộ tài liệu** và **báo cáo tóm tắt** những gì Agent đã hiểu về cấu trúc lab, hệ thống TA_Chatbot, và kế hoạch sẽ thực hiện — trước khi tạo bất kỳ file nào.