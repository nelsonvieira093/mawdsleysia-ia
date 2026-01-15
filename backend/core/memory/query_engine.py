#E:\MAWDSLEYS-AGENTE\backend\core\memory\query_engine.py

from typing import List
from datetime import datetime

from db.models.activity_log import ActivityLog


class QueryEngine:
    """
    Engine responsável por consultas semânticas e temporais
    sobre a memória institucional (activity_logs).
    """

    def __init__(self, events: List[ActivityLog]):
        self.events = events

    def find_by_date(self, date_iso: str) -> List[ActivityLog]:
        """
        Busca eventos ocorridos em uma data específica (ISO).
        Exemplo: '2026-01-04'
        """
        return [
            e for e in self.events
            if date_iso in e.timestamp.isoformat()
        ]

    def find_by_keyword(self, keyword: str) -> List[ActivityLog]:
        """
        Busca eventos que contenham a palavra-chave
        no tipo do evento ou no payload.
        """
        keyword = keyword.lower()

        return [
            e for e in self.events
            if keyword in e.type.lower()
            or keyword in str(e.payload).lower()
        ]

    def find_by_entity(self, entity: str) -> List[ActivityLog]:
        """
        Busca eventos por entidade (meeting, followup, kpi, document, chat).
        """
        return [
            e for e in self.events
            if e.entity == entity
        ]

    def find_between_dates(
        self,
        start: datetime,
        end: datetime
    ) -> List[ActivityLog]:
        """
        Busca eventos entre duas datas.
        """
        return [
            e for e in self.events
            if start <= e.timestamp <= end
        ]
