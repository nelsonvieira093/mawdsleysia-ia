from datetime import datetime
from pydantic import BaseModel
from typing import Dict, Any
from uuid import uuid4

class Alert(BaseModel):
    id: str | None = None
    level: str            # info | warning | critical
    title: str
    description: str
    source_event_id: str
    created_at: datetime | None = None
    payload: Dict[str, Any] = {}

    def __init__(self, **data):
        super().__init__(**data)
        if not self.id:
            self.id = f"alt_{uuid4().hex[:8]}"
        if not self.created_at:
            self.created_at = datetime.utcnow()
