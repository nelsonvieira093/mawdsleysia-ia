# E:\MAWDSLEYS-AGENTE\backend\models\note.py
from sqlalchemy import (
    Column,
    Text,
    DateTime,
    ForeignKey,
    String,
    JSON,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from database.base import Base

class Note(Base):
    __tablename__ = "notes"
    __table_args__ = {'extend_existing': True}
    
    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
    )

    title = Column(String(200), nullable=True)
    content = Column(Text, nullable=False)

    capture_id = Column(
        UUID(as_uuid=True),
        ForeignKey("captures.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        unique=True,
    )

    # ✅ CORREÇÃO CRÍTICA: Mude Integer para UUID
    user_id = Column(
        UUID(as_uuid=True),  # ❌ TROQUE Integer POR UUID
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    note_type = Column(String(50), default="general", nullable=False)
    priority = Column(String(20), default="medium", nullable=False)
    status = Column(String(20), default="draft", nullable=False)

    note_metadata = Column(JSON, default=dict, nullable=False)
    ai_insights = Column(JSON, default=dict, nullable=False)

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    updated_at = Column(
        DateTime(timezone=True),
        onupdate=func.now(),
        nullable=True,
    )

    published_at = Column(DateTime(timezone=True), nullable=True)

    # 🔁 RELACIONAMENTOS CORRIGIDOS
    note_tags = relationship(
        "NoteTag",
        back_populates="note",
        cascade="all, delete-orphan",
        lazy="select",
    )

    tags = relationship(
        "Tag",
        secondary="note_tags",
        primaryjoin="Note.id == NoteTag.note_id",
        secondaryjoin="NoteTag.tag_id == Tag.id",
        viewonly=True,
        lazy="select",
    )

    # ✅ RELAÇÃO CORRIGIDA: Caminho completo para FollowUp
    followups = relationship(
        "database.db_models.FollowUp",  # ✅ CAMINHO COMPLETO
        back_populates="note",
        foreign_keys="database.db_models.FollowUp.note_id",
        cascade="all, delete-orphan",
        lazy="select",
    )

    def __repr__(self):
        return f"<Note id={self.id} title={self.title!r}>"

    def to_dict(self):
        return {
            "id": str(self.id),
            "title": self.title,
            "content": self.content,
            "note_type": self.note_type,
            "status": self.status,
            "priority": self.priority,
            "capture_id": str(self.capture_id),
            "user_id": str(self.user_id),  # ✅ Convertido para string (UUID)
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "published_at": self.published_at.isoformat() if self.published_at else None,
            "ai_insights": self.ai_insights,
            "metadata": self.note_metadata,
        }