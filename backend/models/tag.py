#E:\MAWDSLEYS-AGENTE\backend\models\tag.py

from sqlalchemy import Column, Text
from sqlalchemy.dialects.postgresql import UUID
import uuid

from database.base import Base


class Tag(Base):
    __tablename__ = "tags"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(Text, unique=True, nullable=False)
