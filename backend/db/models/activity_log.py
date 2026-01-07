#E:\MAWDSLEYS-AGENTE\backend\db\models\activity_log.py

from sqlalchemy import Column, String, DateTime, JSON
from datetime import datetime
from db.base import Base


class ActivityLog(Base):
    __tablename__ = "activity_logs"

    id = Column(String, primary_key=True, index=True)
    type = Column(String, index=True)
    entity = Column(String, index=True)
    entity_id = Column(String, index=True)
    actor = Column(String)
    timestamp = Column(DateTime, default=datetime.utcnow)
    payload = Column(JSON)

