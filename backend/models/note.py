# E:\MAWDSLEYS-AGENTE\backend\models\note.py
from sqlalchemy import Column, Text, ForeignKey, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid

from database.base import Base


class Note(Base):
    __tablename__ = "notes"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    created_at = Column(DateTime, server_default=func.now())

    content = Column(Text, nullable=False)
    capture_id = Column(UUID(as_uuid=True), ForeignKey("captures.id"))
    ritual_id = Column(UUID(as_uuid=True), ForeignKey("rituals.id"))
