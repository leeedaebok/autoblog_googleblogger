import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

load_dotenv()

GMAIL_USER = os.getenv("NOTIFY_EMAIL", "")
GMAIL_APP_PASSWORD = os.getenv("GMAIL_APP_PASSWORD", "")


def send_error_email(project_name: str, log_content: str):
    if not GMAIL_USER or not GMAIL_APP_PASSWORD:
        print("⚠️ 이메일 설정 없음 - 전송 건너뜀")
        return

    try:
        msg = MIMEMultipart()
        msg["From"] = GMAIL_USER
        msg["To"] = GMAIL_USER
        msg["Subject"] = f"[AutoBlog 오류] {project_name}"
        msg.attach(MIMEText(log_content, "plain", "utf-8"))

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
            smtp.login(GMAIL_USER, GMAIL_APP_PASSWORD)
            smtp.send_message(msg)

        print(f"📧 에러 메일 발송 완료 → {GMAIL_USER}")
    except Exception as e:
        print(f"⚠️ 이메일 전송 실패: {e}")

