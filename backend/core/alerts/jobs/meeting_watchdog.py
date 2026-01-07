from datetime import datetime
from sqlalchemy.orm import Session

from core.alerts.alert_engine import AlertEngine
from core.events.activity_log import ActivityEvent
from db.repositories.activity_log_repository import ActivityLogRepository
from api.routes.meetings import MeetingController


def check_meetings_not_started(db: Session):
    """
    Verifica reuniões que já deveriam ter começado
    """
    alert_engine = AlertEngine(db)
    now = datetime.utcnow()

    meetings = MeetingController.get_all_meetings(db, skip=0, limit=1000)

    for meeting in meetings:
        if (
            meeting["status"] == "scheduled"
            and meeting["scheduled_time"] <= now
        ):
            alert_engine.emit(
                type="meeting.not_started",
                severity="critical",
                title="Reunião não iniciada no horário",
                message=(
                    f"A reunião '{meeting['title']}' estava agendada para "
                    f"{meeting['scheduled_time']} e não foi iniciada."
                ),
                entity="meeting",
                entity_id=str(meeting["id"]),
                actor="system",
            )
