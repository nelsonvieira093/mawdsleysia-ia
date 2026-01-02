# backend/models/note.py
from sqlalchemy import (
    Column, Integer, Text, DateTime, 
    ForeignKey, JSON, String
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime

from database.session import Base

class Note(Base):
    __tablename__ = "notes"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Conteúdo principal da nota
    content = Column(Text, nullable=False)
    
    # Título/resumo da nota
    title = Column(String(200), nullable=True)
    
    # Referência à captura original
    capture_id = Column(
        Integer,
        ForeignKey("captures.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        unique=True
    )
    
    # Usuário que criou/processou a nota
    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    
    # Tipo de nota
    note_type = Column(
        String(50),
        default="general",
        nullable=False
    )
    
    # Prioridade
    priority = Column(
        String(20),
        default="medium",
        nullable=False
    )
    
    # Status
    status = Column(
        String(20),
        default="draft",
        nullable=False
    )
    
    # Metadados
    note_metadata = Column(JSON, default=dict, nullable=False)
    
    # IA insights
    ai_insights = Column(JSON, default=dict, nullable=False)
    
    # Timestamps
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )
    
    updated_at = Column(
        DateTime(timezone=True),
        onupdate=func.now(),
        nullable=True
    )
    
    published_at = Column(DateTime(timezone=True), nullable=True)
    
    # =========================
    # RELACIONAMENTOS SIMPLIFICADOS
    # =========================
    
    # Relação com Capture (SEM back_populates por enquanto)
    capture = relationship(
        "Capture",
        # back_populates="note",  # ⬅️ COMENTADO até Capture ter note
        uselist=False
    )
    
    # Relação com User
    user = relationship("User")
    
    # Relação com FollowUps
    followups = relationship(
        "FollowUp",
        back_populates="note",
        cascade="all, delete-orphan"
    )
    
    # ⚠️ RELAÇÕES COMENTADAS até modelos existirem:
    # ritual_id = Column(...)  # ⬅️ COMENTE se não tem Ritual
    # ritual = relationship(...)  # ⬅️ COMENTE
    
    # note_tags = relationship(...)  # ⬅️ COMENTE se NoteTag não existe
    # tags = relationship(...)  # ⬅️ COMENTE se Tag não existe
    
    # =========================
    # MÉTODOS
    # =========================
    
    def publish(self):
        self.status = "published"
        self.published_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
    
    def archive(self):
        self.status = "archived"
        self.updated_at = datetime.utcnow()
    
    def add_ai_insight(self, key: str, value):
        if not self.ai_insights:
            self.ai_insights = {}
        self.ai_insights[key] = value
        self.updated_at = datetime.utcnow()
    
    def add_metadata(self, key: str, value):
        if not self.note_metadata:
            self.note_metadata = {}
        self.note_metadata[key] = value
        self.updated_at = datetime.utcnow()
    
    def to_dict(self, include_content: bool = True):
        data = {
            "id": self.id,
            "title": self.title,
            "note_type": self.note_type,
            "priority": self.priority,
            "status": self.status,
            "capture_id": self.capture_id,
            "user_id": self.user_id,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "published_at": self.published_at.isoformat() if self.published_at else None,
            "followups_count": 0,  # ⬅️ Simplificado
            "ai_insights": self.ai_insights,
            "metadata": self.note_metadata
        }
        
        if include_content:
            data["content"] = self.content
            
        return data
    
    def __repr__(self):
        return f"<Note(id={self.id}, title='{self.title}', type='{self.note_type}')>"