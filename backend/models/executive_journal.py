from sqlalchemy import Column, Integer, Text, DateTime, JSON, ForeignKey
from sqlalchemy.sql import func
from database.base import Base

class ExecutiveJournal(Base):
    __tablename__ = "executive_journals"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    summary = Column(Text, nullable=True)
    alerts = Column(JSON, nullable=True)
    followups = Column(JSON, nullable=True)
    actions = Column(JSON, nullable=True)
    decisions = Column(JSON, nullable=True)
    tags = Column(JSON, nullable=True)

    raw_input = Column(Text, nullable=True)
    raw_output = Column(JSON, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
