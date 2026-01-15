# E:\MAWDSLEYS-AGENTE\backend\db\models\sla_config.py

from sqlalchemy import Column, Integer, String
from database.base import Base

class SLAConfig(Base):
    __tablename__ = "sla_configs"

    id = Column(Integer, primary_key=True)
    client_id = Column(Integer, nullable=False)
    alert_type = Column(String, nullable=False)
    max_minutes = Column(Integer, nullable=False)
    notification_channel = Column(String, nullable=False)  # e.g., "email", "whatsapp"
