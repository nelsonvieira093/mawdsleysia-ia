# backend/models/capture.py
from sqlalchemy import (
    Column, Text, Boolean, DateTime, 
    Integer, ForeignKey, JSON, String
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime

from database.session import Base  # ⚠️ MESMO BASE DO USER

class Capture(Base):
    __tablename__ = "captures"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Texto bruto capturado
    raw_text = Column(Text, nullable=False)
    
    # Resumo gerado pela IA
    summary = Column(Text, nullable=True)
    
    # Fonte da captura
    source = Column(String(100), default="api", nullable=False)
    
    # Usuário que fez a captura
    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    
    # Ritual associado (se identificado pela IA)
    ritual_id = Column(
        Integer,
        ForeignKey("rituals.id", ondelete="SET NULL"),
        nullable=True,
        index=True
    )
    
    # Status de processamento
    processed = Column(Boolean, default=False, nullable=False)
    
    # Quando foi processado
    processed_at = Column(DateTime(timezone=True), nullable=True)
    
    # ⚠️ CORREÇÃO: Renomeie 'metadata' para outro nome
    # Metadados adicionais (formato JSON)
    capture_metadata = Column(JSON, default=dict, nullable=False)  # ⬅️ MUDADO AQUI
    
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
    
    # =========================
    # RELACIONAMENTOS
    # =========================
    
    # Relação com User
    user = relationship(
        "User",
        back_populates="captures"
    )
    
    # Relação com Note (se existir)
    # note = relationship(
    #     "Note", 
    #     back_populates="capture",
    #     uselist=False,
    #     cascade="all, delete-orphan"
    # )
    
    # Relação com Ritual
    ritual = relationship(
        "Ritual",
        back_populates="captures"
    )
    
    # =========================
    # MÉTODOS
    # =========================
    
    def mark_as_processed(self):
        """Marca a captura como processada"""
        self.processed = True
        self.processed_at = datetime.utcnow()
    
    def update_summary(self, summary_text: str):
        """Atualiza o resumo da captura"""
        self.summary = summary_text
    
    def add_metadata(self, key: str, value):
        """Adiciona metadados à captura"""
        if not self.capture_metadata:  # ⬅️ MUDADO AQUI
            self.capture_metadata = {}  # ⬅️ MUDADO AQUI
        self.capture_metadata[key] = value  # ⬅️ MUDADO AQUI
    
    def __repr__(self):
        return f"<Capture(id={self.id}, source='{self.source}', processed={self.processed})>"
    
    def to_dict(self):
        """Converte para dicionário (útil para APIs)"""
        return {
            "id": self.id,
            "raw_text": self.raw_text[:100] + "..." if len(self.raw_text) > 100 else self.raw_text,
            "summary": self.summary,
            "source": self.source,
            "user_id": self.user_id,
            "ritual_id": self.ritual_id,
            "processed": self.processed,
            "processed_at": self.processed_at.isoformat() if self.processed_at else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "metadata": self.capture_metadata  # ⬅️ MUDADO AQUI (mantém 'metadata' na API)
        }