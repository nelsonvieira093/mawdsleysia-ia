# backend/database/models.py - VERSÃO FINAL CORRIGIDA
from sqlalchemy import Column, String, Date, DateTime, Text, ForeignKey, Enum as SQLEnum, Integer
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
import enum

from database.base import Base


# Enum para o status
class FollowUpStatus(enum.Enum):
    ABERTO = "ABERTO"
    EM_ANDAMENTO = "EM_ANDAMENTO"
    CONCLUIDO = "CONCLUIDO"


class FollowUp(Base):
    __tablename__ = "followups"

    # ⚠️ ID é UUID (confirmado no banco)
    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True
    )

    # ⚠️ CORREÇÃO CRÍTICA: owner_id deve ser Integer (igual users.id)
    owner_id = Column(
        Integer,  # ✅ MUDAR de UUID para Integer
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    # note_id é UUID (correto)
    note_id = Column(
        UUID(as_uuid=True),
        ForeignKey("notes.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    # Colunas principais
    description = Column(Text, nullable=False)
    due_date = Column(Date, nullable=True)
    
    # Status como Enum
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

    # Colunas extras (opcional)
    ritual_id = Column(
        UUID(as_uuid=True),  # Se rituals.id for UUID
        ForeignKey("rituals.id", ondelete="SET NULL"),
        nullable=True,
    )
    
    source_note_id = Column(
        UUID(as_uuid=True),
        ForeignKey("notes.id", ondelete="SET NULL"),
        nullable=True,
    )

    # 🔁 RELACIONAMENTOS
    note = relationship(
        "Note", 
        foreign_keys=[note_id],
        back_populates="followups",
        lazy="select"
    )
    
    owner = relationship("User", foreign_keys=[owner_id])
    
    # Se tiver modelo Ritual:
    # ritual = relationship("Ritual", foreign_keys=[ritual_id])

    def __repr__(self):
        return f"<FollowUp(id={self.id}, status={self.status.value})>"