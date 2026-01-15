# E:\MAWDSLEYS-AGENTE\backend\core\alerts\alert_engine.py

from typing import List
from sqlalchemy.orm import Session

from core.alerts.alert import Alert
from core.events.activity_log import ActivityEvent
from db.repositories.activity_log_repository import ActivityLogRepository


class AlertEngine:
    def __init__(self, db: Session):
        self.db = db
        self.repo = ActivityLogRepository(db)
    
    async def emit(self, **kwargs):
        """Emite um alerta - aceita 'type' ou 'alert_type' como parâmetro"""
        try:
            # ✅ CORREÇÃO: Aceita tanto 'type' quanto 'alert_type'
            alert_type = kwargs.get('type') or kwargs.get('alert_type')
            message = kwargs.get('message') or kwargs.get('detail') or "Alerta gerado"
            
            if not alert_type:
                print(f"[AlertEngine] ⚠️ Tipo de alerta não especificado: {kwargs}")
                alert_type = "system.alert"
            
            alert = Alert(
                level=kwargs.get('level', 'info'),
                title=kwargs.get('title', alert_type),
                description=message,
                source_event_id=kwargs.get('source_event_id', 'system'),
                payload={
                    "user_id": kwargs.get('user_id'),
                    "entity": kwargs.get('entity'),
                    "message": message,
                    **kwargs
                }
            )
            
            alert_event = ActivityEvent(
                type="alert.created",
                entity="alert",
                entity_id=f"alert_{alert_type}_{id(alert)}",
                actor=kwargs.get('actor', 'ALERT_ENGINE'),
                payload={
                    "level": alert.level,
                    "title": alert.title,
                    "description": alert.description,
                    "source_event_id": alert.source_event_id,
                    "data": alert.payload
                }
            )
            
            await self.repo.save(alert_event)
            print(f"🔔 [AlertEngine] Emitido: {alert_type} - {message}")
            return alert
            
        except Exception as e:
            print(f"[AlertEngine] ❌ Erro no emit: {e}")
            return None

    async def process_event(self, event: ActivityEvent) -> List[Alert]:
        alerts: List[Alert] = []

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

        if event.type == "meeting.completed":
            agenda = event.payload.get("agenda")
            if not agenda or not str(agenda).strip():
                alerts.append(
                    Alert(
                        level="critical",
                        title="Reunião concluída sem ata",
                        description=f"A reunião {event.entity_id} foi concluída sem registro de ata ou agenda.",
                        source_event_id=event.id,
                        payload=event.payload
                    )
                )

        for alert in alerts:
            if alert.level == "critical":
                try:
                    print(f"🔔 [AlertEngine] Alerta crítico: {alert.title}")
                except Exception as e:
                    print(f"[AlertEngine] ❌ Falha ao processar alerta crítico: {e}")

        for alert in alerts:
            try:
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
            except Exception as e:
                print(f"[AlertEngine] ❌ Erro ao salvar alerta: {e}")

        return alerts