from datetime import datetime
from typing import List, Optional
import json

from sqlalchemy.orm import Session
from sqlalchemy import select

from db.models.activity_log import ActivityLog


class ActivityLogRepository:
    def __init__(self, session: Session):
        self.session = session

    async def save(self, event):
        """Salva evento na SUA estrutura do banco"""
        try:
            # Extrai user_id do actor
            user_id = self._extract_user_id(event.actor)

            # Se não conseguir extrair, usa um default (sistema)
            if user_id is None:
                user_id = 0  # ID para sistema/anônimo

            # Prepara os dados para SUA estrutura
            db_data = {
                "user_id": user_id,
                "action": event.type,  # Sua coluna 'action' recebe o type
                "details": json.dumps(event.payload, ensure_ascii=False, default=str),
                "created_at": event.timestamp or datetime.utcnow()
            }

            # Adiciona campos extras se existirem no modelo
            try:
                if hasattr(ActivityLog, 'type'):
                    db_data['type'] = event.type
                if hasattr(ActivityLog, 'entity'):
                    db_data['entity'] = event.entity
                if hasattr(ActivityLog, 'entity_id'):
                    db_data['entity_id'] = event.entity_id
                if hasattr(ActivityLog, 'payload'):
                    db_data['payload'] = event.payload
            except Exception:
                pass  # Ignora se não existir

            # Cria o registro
            db_event = ActivityLog(**db_data)

            self.session.add(db_event)
            self.session.commit()   # ✅ commit síncrono

            # Atualiza o ID no evento original
            event.id = str(db_event.id)

            print(f"[ActivityLogRepository] ✅ Evento salvo: {event.type} (ID: {db_event.id})")
            return db_event

        except Exception as e:
            print(f"[ActivityLogRepository] ❌ Erro ao salvar evento: {e}")
            self.session.rollback()  # ✅ rollback síncrono
            raise

    def _extract_user_id(self, actor: str) -> Optional[int]:
        """Converte actor string para user_id inteiro"""
        try:
            if not actor or actor == "anonymous":
                return None
            elif actor == "system" or actor == "MAWDSLEYS_AI":
                return 0  # Sistema
            elif actor.startswith("user_"):
                return int(actor.split("_")[1])
            elif actor.isdigit():
                return int(actor)
            else:
                import re
                numbers = re.findall(r'\d+', actor)
                if numbers:
                    return int(numbers[0])
                return None
        except Exception:
            return None

    async def list_recent(self, limit: int = 50) -> List[ActivityLog]:
        """Lista eventos recentes"""
        result = self.session.execute(
            select(ActivityLog)
            .order_by(ActivityLog.created_at.desc())
            .limit(limit)
        )
        return result.scalars().all()

    async def list_since(self, since: datetime) -> List[ActivityLog]:
        """Lista eventos desde uma data"""
        result = self.session.execute(
            select(ActivityLog)
            .where(ActivityLog.created_at >= since)
            .order_by(ActivityLog.created_at.desc())
        )
        return result.scalars().all()

    def to_activity_event(self, db_log: ActivityLog) -> dict:
        """Converte do banco para formato ActivityEvent"""
        try:
            details = json.loads(db_log.details) if db_log.details else {}
        except Exception:
            details = {"raw": db_log.details}

        if db_log.user_id == 0:
            actor = "system"
        elif db_log.user_id:
            actor = f"user_{db_log.user_id}"
        else:
            actor = "anonymous"

        return {
            "id": str(db_log.id),
            "type": db_log.action or getattr(db_log, 'type', 'unknown'),
            "entity": getattr(db_log, 'entity', 'unknown'),
            "entity_id": getattr(db_log, 'entity_id', str(db_log.id)),
            "actor": actor,
            "timestamp": db_log.created_at,
            "payload": getattr(db_log, 'payload', details) or details
        }

    # =====================================================
    # 🔴 LEITURA DE ALERTAS CRÍTICOS (NOVA FUNCIONALIDADE)
    # =====================================================
    from datetime import timedelta

    async def list_critical_alerts(self, days: int = 1):
        """
        Retorna alertas críticos recentes
        (eventos alert.created com level=critical)
        """
        since = datetime.utcnow() - self.timedelta(days=days)

        result = self.session.execute(
            select(ActivityLog)
            .where(ActivityLog.action == "alert.created")
            .where(ActivityLog.created_at >= since)
            .order_by(ActivityLog.created_at.desc())
        )

        alerts = []
        for row in result.scalars():
            try:
                details = json.loads(row.details) if row.details else {}
                if details.get("level") == "critical":
                    alerts.append(row)
            except Exception:
                continue

        return alerts
