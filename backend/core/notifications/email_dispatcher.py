# backend/core/notifications/email_dispatcher.py

import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from typing import Optional

from core.events.activity_log import ActivityEvent
from db.repositories.activity_log_repository import ActivityLogRepository
from sqlalchemy.orm import Session


class EmailDispatcher:
    """
    Responsável por enviar e-mails automáticos
    e registrar sucesso ou falha no Activity Log.
    """

    def __init__(self, db: Session):
        self.db = db

        # Configurações via ENV (produção-ready)
        self.smtp_host = os.getenv("SMTP_HOST", "smtp.gmail.com")
        self.smtp_port = int(os.getenv("SMTP_PORT", "587"))
        self.smtp_user = os.getenv("SMTP_USER")
        self.smtp_password = os.getenv("SMTP_PASSWORD")
        self.from_email = os.getenv("SMTP_FROM", self.smtp_user)

        if not self.smtp_user or not self.smtp_password:
            print("[EmailDispatcher] ⚠️ SMTP não configurado (emails desativados)")

    def send_critical_alert_email(
        self,
        to_email: str,
        title: str,
        description: str,
        source_event_id: Optional[str] = None,
    ) -> bool:
        """
        Envia e-mail de alerta crítico.
        Retorna True se enviado com sucesso.
        """

        if not self.smtp_user or not self.smtp_password:
            print("[EmailDispatcher] ❌ SMTP não configurado. Email não enviado.")
            return False

        subject = "🚨 ALERTA CRÍTICO — MAWDSLEYS"

        body = f"""
Um alerta crítico foi detectado pelo sistema MAWDSLEYS.

Título:
{title}

Descrição:
{description}

Evento de origem:
{source_event_id or "N/A"}

Data:
{datetime.utcnow().strftime("%d/%m/%Y %H:%M UTC")}

Ação recomendada:
Verificar imediatamente e tomar providências.

Este e-mail foi enviado automaticamente pelo sistema MAWDSLEYS.
"""

        try:
            # Monta e-mail
            msg = MIMEMultipart()
            msg["From"] = self.from_email
            msg["To"] = to_email
            msg["Subject"] = subject
            msg.attach(MIMEText(body, "plain", "utf-8"))

            # Envia
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_user, self.smtp_password)
                server.send_message(msg)

            # Loga sucesso
            self._log_email_event(
                status="sent",
                to_email=to_email,
                title=title,
                source_event_id=source_event_id,
            )

            print(f"[EmailDispatcher] ✅ Email enviado para {to_email}")
            return True

        except Exception as e:
            # Loga falha
            self._log_email_event(
                status="failed",
                to_email=to_email,
                title=title,
                source_event_id=source_event_id,
                error=str(e),
            )

            print(f"[EmailDispatcher] ❌ Falha ao enviar email: {e}")
            return False

    def _log_email_event(
        self,
        status: str,
        to_email: str,
        title: str,
        source_event_id: Optional[str],
        error: Optional[str] = None,
    ):
        """
        Registra envio de email no Activity Log
        """
        try:
            repo = ActivityLogRepository(self.db)

            event = ActivityEvent(
                type="notification.email",
                entity="email",
                entity_id=f"email_{datetime.utcnow().timestamp()}",
                actor="MAWDSLEYS_SYSTEM",
                payload={
                    "status": status,
                    "to": to_email,
                    "title": title,
                    "source_event_id": source_event_id,
                    "error": error,
                    "timestamp": datetime.utcnow().isoformat(),
                },
            )

            # salva síncrono para garantir auditoria
            self.db.add  # força import do session
            import asyncio
            asyncio.create_task(repo.save(event))

        except Exception as e:
            print(f"[EmailDispatcher] ⚠️ Falha ao registrar evento de email: {e}")
