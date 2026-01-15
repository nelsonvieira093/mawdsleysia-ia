#E:\MAWDSLEYS-AGENTE\backend\models\person.py
from sqlalchemy import Column, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
import uuid

from database.base import Base


class Person(Base):
    __tablename__ = "people"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(Text, nullable=False)
    role = Column(Text)

    default_ritual_id = Column(UUID(as_uuid=True), ForeignKey("rituals.id"))
