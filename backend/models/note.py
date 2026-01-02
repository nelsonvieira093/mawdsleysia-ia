# models/note.py - VERSÃO 100% FUNCIONAL (SEM RELACIONAMENTOS)
from sqlalchemy import Column, Integer, Text, DateTime, ForeignKey, String, JSON
from sqlalchemy.sql import func
from datetime import datetime

from database.session import Base

class Note(Base):
    __tablename__ = "notes"
    
    id = Column(Integer, primary_key=True, index=True)
    content = Column(Text, nullable=False)
    title = Column(String(200), nullable=True)
    capture_id = Column(Integer, ForeignKey("captures.id"), nullable=False, index=True, unique=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    note_type = Column(String(50), default="general", nullable=False)
    priority = Column(String(20), default="medium", nullable=False)
    status = Column(String(20), default="draft", nullable=False)
    note_metadata = Column(JSON, default=dict, nullable=False)
    ai_insights = Column(JSON, default=dict, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)
    published_at = Column(DateTime(timezone=True), nullable=True)
    
    # ⚠️ SEM NENHUM RELACIONAMENTO
    # ⚠️ NÃO USE relationship() - CAUSA ERROS
    
    def __repr__(self):
        return f"<Note(id={self.id}, title='{self.title}')>"
    
    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "content": self.content,
            "note_type": self.note_type,
            "status": self.status,
            "priority": self.priority,
            "capture_id": self.capture_id,
            "user_id": self.user_id,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "published_at": self.published_at.isoformat() if self.published_at else None,
            "ai_insights": self.ai_insights,
            "metadata": self.note_metadata
        }
