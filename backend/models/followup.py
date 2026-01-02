# backend/models/followup.py
from sqlalchemy import (
    Column, Integer, Text, Date, Enum, 
    ForeignKey, DateTime, String
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from database.session import Base

class FollowUp(Base):  # NOTE: Mantenha FollowUp (com U maiúsculo)
    __tablename__ = "followups"

    id = Column(Integer, primary_key=True, index=True)
    
    # Referência ao User
    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    
    # Referência à Note (se existir)
    note_id = Column(
        Integer,
        ForeignKey("notes.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )
    
    # Referência ao Ritual (se existir)
    ritual_id = Column(
        Integer,
        ForeignKey("rituals.id", ondelete="SET NULL"),
        nullable=True,
    )
    
    # Referência à Person (responsável)
    owner_id = Column(
        Integer,
        ForeignKey("people.id", ondelete="SET NULL"),
        nullable=True,
    )
    
    title = Column(String(200), nullable=True)
    description = Column(Text, nullable=False)
    
    due_date = Column(Date)
    
    status = Column(
        Enum(
            "ABERTO",
            "EM_ANDAMENTO",
            "CONCLUIDO",
            "CANCELADO",
            name="followup_status",
        ),
        default="ABERTO",
        nullable=False,
    )
    
    priority = Column(
        Enum(
            "BAIXA",
            "MEDIA", 
            "ALTA",
            "URGENTE",
            name="followup_priority",
        ),
        default="MEDIA",
        nullable=False,
    )
    
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

    # =========================
    # RELACIONAMENTOS
    # =========================
    user = relationship(
        "User",
        back_populates="followups",
    )
    
    # note = relationship("Note", back_populates="followups")  # Se existir
    # ritual = relationship("Ritual", back_populates="followups")  # Se existir
    # owner = relationship("Person", back_populates="assigned_followups")  # Se existir

    def __repr__(self):
        return f"<FollowUp(id={self.id}, status='{self.status}')>"