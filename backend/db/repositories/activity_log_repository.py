from datetime import datetime, timedelta
from typing import List, Optional

from sqlalchemy.orm import Session
from sqlalchemy import select

from db.models.activity_log import ActivityLog


class ActivityLogRepository:
    def __init__(self, session: Session):
        self.session = session

    # =====================================================
    # SAVE
    # =====================================================
    async def save(self, event) -> ActivityLog:
        """
        Salva evento EXATAMENTE conforme a tabela activity_logs.

        ⚠️ IMPORTANTE:
        - A tabela NÃO possui coluna 'actor'
        - 'actor' é usado SOMENTE em memória
        """

        try:
            # Extrai user_id APENAS para uso no banco
            user_id = self._extract_user_id(getattr(event, "actor", None))
            if user_id is None:
                user_id = 0

            db_event = ActivityLog(
    type=str(event.type),
    entity=str(event.entity),
    entity_id=str(event.entity_id),
    user_id=user_id,
    created_at=event.timestamp or datetime.utcnow(),
    payload=event.payload if isinstance(event.payload, dict) else {},
    action=str(event.type),
)



            self.session.add(db_event)
            self.session.commit()

            # Atualiza ID no objeto em memória (não afeta o banco)
            event.id = db_event.id

            print(
                f"[ActivityLogRepository] ✅ Evento salvo: "
                f"type={db_event.type} user_id={db_event.user_id}"
            )

            return db_event

        except Exception as e:
            self.session.rollback()
            print(f"[ActivityLogRepository] ❌ Erro ao salvar evento: {e}")
            raise

    # =====================================================
    # USER ID EXTRACTION
    # =====================================================
    def _extract_user_id(self, actor: Optional[str]) -> Optional[int]:
        """
        Converte actor lógico para user_id inteiro.

        Aceita:
        - user_123
        - 123
        - system
        - MAWDSLEYS_AI
        """

        try:
            if not actor or actor == "anonymous":
                return None

            if actor in ("system", "MAWDSLEYS_AI"):
                return 0

            if isinstance(actor, str):
                if actor.startswith("user_"):
                    return int(actor.split("_")[1])

                if actor.isdigit():
                    return int(actor)

                import re
                numbers = re.findall(r"\d+", actor)
                if numbers:
                    return int(numbers[0])

            return None

        except Exception:
            return None

    # =====================================================
    # READ METHODS
    # =====================================================
    async def list_recent(self, limit: int = 50) -> List[ActivityLog]:
        result = self.session.execute(
            select(ActivityLog)
            .order_by(ActivityLog.timestamp.desc())
            .limit(limit)
        )
        return result.scalars().all()

    async def list_since(self, since: datetime) -> List[ActivityLog]:
        result = self.session.execute(
            select(ActivityLog)
            .where(ActivityLog.timestamp >= since)
            .order_by(ActivityLog.timestamp.desc())
        )
        return result.scalars().all()

    # =====================================================
    # CRITICAL ALERTS
    # =====================================================
    async def list_critical_alerts(self, days: int = 1) -> List[ActivityLog]:
        """
        Retorna alertas críticos recentes
        (type = 'alert.created' e payload.level = 'critical')
        """

        since = datetime.utcnow() - timedelta(days=days)

        result = self.session.execute(
            select(ActivityLog)
            .where(ActivityLog.type == "alert.created")
            .where(ActivityLog.timestamp >= since)
            .order_by(ActivityLog.timestamp.desc())
        )

        alerts: List[ActivityLog] = []

        for row in result.scalars():
            payload = row.payload or {}
            if isinstance(payload, dict) and payload.get("level") == "critical":
                alerts.append(row)

        return alerts
