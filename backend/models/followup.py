from sqlalchemy import Column, Text, Date, Enum, ForeignKey, TIMESTAMP
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid

from database.base import Base

class FollowUp(Base):
    __tablename__ = "followups"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    description = Column(Text, nullable=False)
    owner_id = Column(UUID(as_uuid=True), ForeignKey("people.id"))
    ritual_id = Column(UUID(as_uuid=True), ForeignKey("rituals.id"))
    due_date = Column(Date)
    status = Column(Enum("ABERTO", "EM_ANDAMENTO", "CONCLUIDO", name="followup_status"))
    source_note_id = Column(UUID(as_uuid=True), ForeignKey("notes.id"))
