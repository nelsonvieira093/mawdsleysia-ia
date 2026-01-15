from datetime import datetime
from sqlalchemy.orm import Session

from core.alerts.alert_engine import AlertEngine
from core.events.activity_log import ActivityEvent
from db.repositories.activity_log_repository import ActivityLogRepository

# ⚠️ IMPORT REAL DO SEU SISTEMA (AJUSTE SE NECESSÁRIO)
from controllers.meeting import get_meetings as db_get_meetings


def check_meetings_not_started(db: Session):
    """
    Watchdog:
    Verifica reuniões agendadas que já deveriam ter iniciado
    e dispara eventos para o AlertEngine.
    """

    now = datetime.utcnow()
    alert_engine = AlertEngine(db)
    repo = ActivityLogRepository(db)

    # Busca reuniões do banco (todas)
    meetings = db_get_meetings(
        db=db,
        user_id=None,   # watchdog é sistêmico
        skip=0,
        limit=1000,
        status="scheduled"
    )

    for meeting in meetings:
        try:
            scheduled_time = meeting.scheduled_time

            if scheduled_time and scheduled_time <= now:
                # 🔹 CRIA EVENTO PADRÃO DO SISTEMA
                event = ActivityEvent(
                    type="meeting.not_started",
                    entity="meeting",
                    entity_id=str(meeting.id),
                    actor="system",
                    payload={
                        "title": meeting.title,
                        "scheduled_time": scheduled_time.isoformat(),
                        "checked_at": now.isoformat()
                    }
                )

                # 🔹 REGISTRA EVENTO
                # (o AlertEngine vai gerar alert.created + email + whatsapp)
                import asyncio
                asyncio.create_task(repo.save(event))
                asyncio.create_task(alert_engine.process_event(event))

                print(
                    f"[MeetingWatchdog] 🚨 Reunião não iniciada detectada "
                    f"(ID: {meeting.id})"
                )

        except Exception as e:
            print(
                f"[MeetingWatchdog] ❌ Erro ao processar reunião "
                f"{getattr(meeting, 'id', 'N/A')}: {e}"
            )
