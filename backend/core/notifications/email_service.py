import os
import smtplib
from email.message import EmailMessage

class EmailService:
    def __init__(self):
        self.host = os.getenv("SMTP_HOST")
        self.port = int(os.getenv("SMTP_PORT", 587))
        self.user = os.getenv("SMTP_USER")
        self.password = os.getenv("SMTP_PASSWORD")
        self.from_email = os.getenv("SMTP_FROM")

        if not all([self.host, self.port, self.user, self.password, self.from_email]):
            raise RuntimeError("Configurações SMTP incompletas")

    def send_alert_email(self, subject: str, body: str, to: str):
        msg = EmailMessage()
        msg["From"] = self.from_email
        msg["To"] = to
        msg["Subject"] = subject
        msg.set_content(body)

        with smtplib.SMTP(self.host, self.port) as server:
            server.starttls()
            server.login(self.user, self.password)
            server.send_message(msg)

        print(f"[EmailService] 📧 Email enviado para {to}")
