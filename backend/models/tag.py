from sqlalchemy import Column, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid

from database.base import Base  # ⚠️ MESMA BASE DO note.py

class Tag(Base):
    __tablename__ = "tags"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), unique=True, nullable=False, index=True)  # ⚠️ MUDAR para String

    # relacionamento reverso
    note_tags = relationship(
        "NoteTag",
        back_populates="tag",
        cascade="all, delete-orphan"
    )

    # Acesso direto às notas (opcional)
    notes = relationship(
        "Note",
        secondary="note_tags",  # ⚠️ NECESSÁRIO se houver tabela de associação
        back_populates="tags",
        lazy="select",
        viewonly=True,
    )