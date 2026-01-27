from sqlalchemy import (
    Column,
    String,
    Date,
    DateTime,
    Text,
    ForeignKey,
    Enum as SQLEnum,
    Integer,
    Boolean,
    JSON,
)
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
import enum

from database.base import Base


# =========================
# ENUMS
# =========================

class FollowUpStatus(enum.Enum):
    ABERTO = "ABERTO"
    EM_ANDAMENTO = "EM_ANDAMENTO"
    CONCLUIDO = "CONCLUIDO"


# =========================
# MODELS
# =========================

class User(Base):
    __tablename__ = "users"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True
    )

    name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    password = Column(String(255), nullable=False)

    is_active = Column(Boolean, default=True, nullable=False)
    is_admin = Column(Boolean, default=False)

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=True,
    )

    def __repr__(self):
        return f"<User id={self.id} email={self.email}>"


class Note(Base):
    __tablename__ = "notes"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True
    )

    content = Column(Text, nullable=False)

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    followups = relationship(
        "FollowUp",
        back_populates="note",
        lazy="select"
    )

    def __repr__(self):
        return f"<Note id={self.id}>"


class FollowUp(Base):
    __tablename__ = "followups"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True
    )

    owner_id = Column(
        UUID(as_uuid=True),  # 🔴 CORREÇÃO CRÍTICA
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    note_id = Column(
        UUID(as_uuid=True),
        ForeignKey("notes.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    description = Column(Text, nullable=False)
    due_date = Column(Date, nullable=True)

    status = Column(
        SQLEnum(FollowUpStatus, name="followup_status"),
        default=FollowUpStatus.ABERTO,
        nullable=False
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=True,
    )

    ritual_id = Column(
        UUID(as_uuid=True),
        ForeignKey("rituals.id", ondelete="SET NULL"),
        nullable=True,
    )

    source_note_id = Column(
        UUID(as_uuid=True),
        ForeignKey("notes.id", ondelete="SET NULL"),
        nullable=True,
    )

    note = relationship(
        "Note",
        foreign_keys=[note_id],
        back_populates="followups",
        lazy="select"
    )

    owner = relationship("User", foreign_keys=[owner_id])

    def __repr__(self):
        return f"<FollowUp(id={self.id}, status={self.status.value})>"
