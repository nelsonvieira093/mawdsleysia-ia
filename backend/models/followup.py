# backend/models/followup.py
from sqlalchemy import (
    Column, Integer, Text, Date,
    ForeignKey, DateTime, String
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from database.session import Base

class FollowUp(Base):
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
    
    title = Column(String(200), nullable=True)
    description = Column(Text, nullable=False)
    
    due_date = Column(Date, nullable=True)
    
    status = Column(
        String(20),  # ⬅️ Mude de Enum para String para simplificar
        default="ABERTO",
        nullable=False,
    )
    
    priority = Column(
        String(20),  # ⬅️ Mude de Enum para String para simplificar
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
    # RELACIONAMENTOS SIMPLIFICADOS
    # =========================
    user = relationship(
        "User",
        back_populates="followups",
    )
    
    # ⚠️ RELAÇÃO com Note COMENTADA (Note não tem back_populates correto)
    # note = relationship("Note")  # SEM back_populates
    
    # ❌ REMOVIDO: ritual_id e owner_id (modelos podem não existir)
    # ❌ REMOVIDO: relacionamentos com Ritual e Person

    def __repr__(self):
        return f"<FollowUp(id={self.id}, status='{self.status}')>"
    
    def to_dict(self):
        """Converte para dicionário"""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "note_id": self.note_id,
            "title": self.title,
            "description": self.description,
            "due_date": self.due_date.isoformat() if self.due_date else None,
            "status": self.status,
            "priority": self.priority,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }