from sqlalchemy import Column, Text
from sqlalchemy.dialects.postgresql import UUID
import uuid

from database.base import Base


class Ritual(Base):
    __tablename__ = "rituals"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    code = Column(Text, unique=True, nullable=False)
    name = Column(Text, nullable=False)
