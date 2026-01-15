#E:\MAWDSLEYS-AGENTE\backend\core\events\activiy_log.py

from datetime import datetime
from typing import Any, Dict
from pydantic import BaseModel
from uuid import uuid4

class ActivityEvent(BaseModel):
    id: str | None = None
    type: str                  # ex: meeting.created, followup.completed
    entity: str                # meeting, kpi, deliverable, document
    entity_id: str             # id da entidade
    actor: str                 # quem gerou a ação (CEO, IA, Sistema)
    timestamp: datetime | None = None
    payload: Dict[str, Any]    # dados livres do evento

    def __init__(self, **data):
        super().__init__(**data)
        if not self.id:
            self.id = f"evt_{uuid4().hex[:8]}"
        if not self.timestamp:
            self.timestamp = datetime.utcnow()
