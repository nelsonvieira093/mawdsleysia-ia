# E:\MAWDSLEYS-AGENTE\backend\core\alerts\sla_engine.py

from datetime import datetime, timedelta

class SLAEngine:
    def __init__(self, minutes: int = 15):
        self.deadline = timedelta(minutes=minutes)

    def is_violated(self, created_at: datetime) -> bool:
        return datetime.utcnow() >= (created_at + self.deadline)
