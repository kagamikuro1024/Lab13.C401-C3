import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def send_escalation_email(report_content: str, to_email: str = "26ai.trunglvq@vinuni.edu.vn") -> bool:
    """
    Gửi email cho TA thông qua SMTP (thay thế cho nodemailer trong Python).
    
    Args:
        report_content (str): Nội dung phiếu escalation.
        to_email (str): Địa chỉ email của TA (mặc định: 26ai.trunglvq@vinuni.edu.vn).
        
    Returns:
        bool: True nếu gửi thành công, False nếu thất bại.
    """
    # Lấy thông tin từ biến môi trường (đã được nạp từ .env bởi config.py)
    sender_email = os.environ.get("EMAIL_USER")
    sender_password = os.environ.get("EMAIL_PASS")
    
    if not sender_email or not sender_password:
        print("Lỗi: Không tìm thấy EMAIL_USER hoặc EMAIL_PASS trong .env")
        return False
        
    # Tạo nội dung email
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = to_email
    msg['Subject'] = "[Khẩn cấp] AI Trợ Giảng - Yêu cầu hỗ trợ từ Học viên"
    
    # Định dạng html hoặc text
    body = f"""
    Thân gửi TA,
    
    Hệ thống AI Trợ Giảng vừa nhận được một yêu cầu leo thang (escalation) từ học viên.
    Vui lòng xem chi tiết phiếu hỗ trợ bên dưới:
    
    {report_content}
    
    Trân trọng,
    Hệ thống AI Trợ Giảng CS101
    """
    msg.attach(MIMEText(body, 'plain', 'utf-8'))
    
    try:
        # Cấu hình SMTP server (Dùng Gmail theo email trong .env)
        # Vì email trong .env là @gmail.com nên dùng smtp.gmail.com
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        # Đăng nhập
        server.login(sender_email, sender_password)
        # Gửi email
        server.send_message(msg)
        server.quit()
        return True
    except Exception as e:
        print(f"Lỗi khi gửi email: {e}")
        return False
