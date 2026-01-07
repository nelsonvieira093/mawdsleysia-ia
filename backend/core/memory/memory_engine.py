# backend/core/memory/memory_engine.py

from sqlalchemy.orm import Session
from typing import List
from db.models.activity_log import ActivityLog

class MemoryEngine:
    def __init__(self, db: Session):
        self.db = db

    def recent_events(self, limit: int = 20) -> List[ActivityLog]:
        """
        Retorna os eventos mais recentes do sistema
        """
        return (
            self.db.query(ActivityLog)
            .order_by(ActivityLog.timestamp.desc())
            .limit(limit)
            .all()
        )

    def search_events(self, keyword: str, limit: int = 10) -> List[ActivityLog]:
        """
        Busca eventos por palavra-chave
        """
        return (
            self.db.query(ActivityLog)
            .filter(
                ActivityLog.type.ilike(f"%{keyword}%") |
                ActivityLog.entity.ilike(f"%{keyword}%")
            )
            .order_by(ActivityLog.timestamp.desc())
            .limit(limit)
            .all()
        )

    def format_for_llm(self, events: List[ActivityLog]) -> str:
        """
        Formata memória para ser enviada ao LLM
        """
        lines = []
        for e in events:
            lines.append(
                f"[{e.timestamp}] {e.type} | {e.entity} | {e.payload}"
            )
        return "\n".join(lines)
