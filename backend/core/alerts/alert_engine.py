from typing import List
from sqlalchemy.orm import Session

from core.alerts.alert import Alert
from core.events.activity_log import ActivityEvent
from db.repositories.activity_log_repository import ActivityLogRepository


class AlertEngine:
    def __init__(self, db: Session):
        self.db = db
        self.repo = ActivityLogRepository(db)

    async def process_event(self, event: ActivityEvent) -> List[Alert]:
        alerts: List[Alert] = []

        # ===============================
        # 🔴 FOLLOW-UP CRÍTICO
        # ===============================
        if event.type == "followup.generated":
            urgency = event.payload.get("urgency")
            if urgency in ("high", "critical"):
                alerts.append(
                    Alert(
                        level="critical",
                        title="Follow-up crítico gerado",
                        description=f"Tarefa crítica atribuída a {event.payload.get('responsible')}",
                        source_event_id=event.id,
                        payload=event.payload
                    )
                )

        # ===============================
        # 🟠 REUNIÃO CANCELADA
        # ===============================
        if event.type == "meeting.cancelled":
            alerts.append(
                Alert(
                    level="warning",
                    title="Reunião cancelada",
                    description="Uma reunião estratégica foi cancelada.",
                    source_event_id=event.id,
                    payload=event.payload
                )
            )

        # ===============================
        # 🔴 KPI REGULATÓRIO
        # ===============================
        if event.type == "kpi.updated":
            area = event.payload.get("area")
            status = event.payload.get("status")
            if area == "Regulatório" and status in ("alert", "critical"):
                alerts.append(
                    Alert(
                        level="critical",
                        title="Alerta regulatório",
                        description="Indicador regulatório em estado crítico.",
                        source_event_id=event.id,
                        payload=event.payload
                    )
                )

        # ===============================
        # 🔴 REUNIÃO CONCLUÍDA SEM ATA
        # ===============================
        if event.type == "meeting.completed":
            agenda = event.payload.get("agenda")

            if not agenda or not str(agenda).strip():
                alerts.append(
                    Alert(
                        level="critical",
                        title="Reunião concluída sem ata",
                        description=(
                            f"A reunião {event.entity_id} foi concluída "
                            f"sem registro de ata ou agenda."
                        ),
                        source_event_id=event.id,
                        payload=event.payload
                    )
                )

        # ===============================
        # REGISTRA ALERTAS COMO EVENTOS
        # ===============================
        for alert in alerts:
            alert_event = ActivityEvent(
                type="alert.created",
                entity="alert",
                entity_id=alert.id,
                actor="ALERT_ENGINE",
                payload={
                    "level": alert.level,
                    "title": alert.title,
                    "description": alert.description,
                    "source_event_id": alert.source_event_id,
                    "data": alert.payload
                }
            )
            await self.repo.save(alert_event)

        return alerts
