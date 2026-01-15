"""
Email Service — PRODUÇÃO
Responsável por envio de emails transacionais e convites de reunião
"""

import smtplib
from email.message import EmailMessage
from typing import List, Optional
import logging

from core.config import settings

logger = logging.getLogger(__name__)


class EmailService:

    @staticmethod
    def send_email(
        *,
        subject: str,
        body: str,
        to: List[str],
        attachments: Optional[list[tuple[str, bytes, str]]] = None,
    ):
        msg = EmailMessage()
        msg["From"] = settings.SMTP_FROM
        msg["To"] = ", ".join(to)
        msg["Subject"] = subject
        msg.set_content(body)

        if attachments:
            for filename, content, mime in attachments:
                maintype, subtype = mime.split("/")
                msg.add_attachment(
                    content,
                    maintype=maintype,
                    subtype=subtype,
                    filename=filename,
                )

        try:
            with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
                server.starttls()
                server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
                server.send_message(msg)
        except Exception as e:
            logger.exception("Erro ao enviar email")
            raise RuntimeError("Falha ao enviar email") from e
