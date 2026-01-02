# backend/models/note.py
from sqlalchemy import (
    Column, Integer, Text, DateTime, 
    ForeignKey, JSON, String
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime

from database.session import Base  # ⚠️ MESMO BASE DOS OUTROS MODELS

class Note(Base):
    __tablename__ = "notes"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Conteúdo principal da nota (texto processado/estruturado)
    content = Column(Text, nullable=False)
    
    # Título/resumo da nota
    title = Column(String(200), nullable=True)
    
    # Referência à captura original (uma note por capture)
    capture_id = Column(
        Integer,
        ForeignKey("captures.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        unique=True  # Garante que cada capture tenha apenas uma note
    )
    
    # Ritual associado (onde esta nota será usada)
    ritual_id = Column(
        Integer,
        ForeignKey("rituals.id", ondelete="SET NULL"),
        nullable=True,
        index=True
    )
    
    # Usuário que criou/processou a nota
    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    
    # Tipo de nota (ex: action_item, decision, reflection, todo)
    note_type = Column(
        String(50),
        default="general",
        nullable=False
    )
    
    # Relação com NoteTag
    note_tags = relationship(
        "NoteTag",
        back_populates="note",
        cascade="all, delete-orphan"
    )
    
    # Prioridade (baixa, média, alta, crítica)
    priority = Column(
        String(20),
        default="medium",
        nullable=False
    )
    
    # Status (draft, published, archived)
    status = Column(
        String(20),
        default="draft",
        nullable=False
    )
    
    # ⚠️ CORREÇÃO: Renomeado de 'metadata' para 'note_metadata'
    # Metadados adicionais (formato JSON)
    note_metadata = Column(JSON, default=dict, nullable=False)
    
    # IA insights (extrações da IA)
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
    # RELACIONAMENTOS
    # =========================
    
    # Relação com Capture (um-para-um)
    capture = relationship(
        "Capture",
        back_populates="note",  # Adicione back_populates no Capture
        uselist=False
    )
    
    # Relação com Ritual
    ritual = relationship(
        "Ritual",
        back_populates="notes"
    )
    
    # Relação com User
    user = relationship(
        "User"
        # back_populates="notes" se adicionar no User
    )
    
    # Relação com FollowUps (uma note pode ter vários followups)
    followups = relationship(
        "FollowUp",
        back_populates="note",
        cascade="all, delete-orphan"
    )
    
    # Relação com Tags (many-to-many)
    tags = relationship(
        "Tag",
        secondary="note_tags",  # Tabela de associação
        back_populates="notes"
    )
    
    # =========================
    # MÉTODOS
    # =========================
    
    def publish(self):
        """Publica a nota"""
        self.status = "published"
        self.published_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
    
    def archive(self):
        """Arquiva a nota"""
        self.status = "archived"
        self.updated_at = datetime.utcnow()
    
    def add_tag(self, tag):
        """Adiciona uma tag à nota"""
        if tag not in self.tags:
            self.tags.append(tag)
    
    def remove_tag(self, tag):
        """Remove uma tag da nota"""
        if tag in self.tags:
            self.tags.remove(tag)
    
    def add_ai_insight(self, key: str, value):
        """Adiciona um insight da IA"""
        if not self.ai_insights:
            self.ai_insights = {}
        self.ai_insights[key] = value
        self.updated_at = datetime.utcnow()
    
    def add_metadata(self, key: str, value):
        """Adiciona metadados à nota"""
        if not self.note_metadata:
            self.note_metadata = {}
        self.note_metadata[key] = value
        self.updated_at = datetime.utcnow()
    
    def get_followups_by_status(self, status: str = None):
        """Retorna followups filtrados por status"""
        if status:
            return [fu for fu in self.followups if fu.status == status]
        return self.followups
    
    def to_dict(self, include_content: bool = True):
        """Converte para dicionário (útil para APIs)"""
        data = {
            "id": self.id,
            "title": self.title,
            "note_type": self.note_type,
            "priority": self.priority,
            "status": self.status,
            "capture_id": self.capture_id,
            "ritual_id": self.ritual_id,
            "user_id": self.user_id,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "published_at": self.published_at.isoformat() if self.published_at else None,
            "tags": [tag.name for tag in self.tags],
            "followups_count": len(self.followups),
            "ai_insights": self.ai_insights,
            "metadata": self.note_metadata  # ⚠️ Atualizado para usar note_metadata
        }
        
        if include_content:
            data["content"] = self.content
            
        return data
    
    def __repr__(self):
        return f"<Note(id={self.id}, title='{self.title}', type='{self.note_type}')>"
    
    @property
    def has_followups(self):
        """Retorna True se a nota tem followups"""
        return len(self.followups) > 0
    
    @property
    def open_followups(self):
        """Retorna followups abertos"""
        return [fu for fu in self.followups if fu.status in ["ABERTO", "EM_ANDAMENTO"]]
    
    @property
    def is_published(self):
        """Retorna True se a nota está publicada"""
        return self.status == "published"