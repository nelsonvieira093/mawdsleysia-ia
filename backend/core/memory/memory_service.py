from typing import List
from datetime import datetime, timedelta

from db.models.activity_log import ActivityLog
from db.repositories.activity_log_repository import ActivityLogRepository
from core.memory.query_engine import QueryEngine


class MemoryService:
    """
    Serviço central de memória institucional.
    """

    def __init__(self, repository: ActivityLogRepository):
        self.repository = repository

    async def load_recent_events(
        self,
        days: int = 30
    ) -> List[ActivityLog]:
        """
        Carrega eventos recentes (default: últimos 30 dias).
        """
        since = datetime.utcnow() - timedelta(days=days)
        return await self.repository.list_since(since)

    async def query(
        self,
        question: str,
        days: int = 90
    ) -> List[ActivityLog]:
        """
        Consulta inteligente baseada em texto livre.
        """
        events = await self.load_recent_events(days=days)
        engine = QueryEngine(events)

        # Estratégia simples (robusta e previsível)
        keyword = question.lower()

        if "reuni" in keyword:
            return engine.find_by_entity("meeting")

        if "follow" in keyword:
            return engine.find_by_entity("followup")

        if "kpi" in keyword or "indicador" in keyword:
            return engine.find_by_entity("kpi")

        if "document" in keyword:
            return engine.find_by_entity("document")

        # fallback semântico
        return engine.find_by_keyword(keyword)
