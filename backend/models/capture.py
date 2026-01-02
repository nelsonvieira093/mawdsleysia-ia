# backend/models/capture.py
from sqlalchemy import (
    Column,
    Text,
    Boolean,
    DateTime,
    Integer,
    ForeignKey,
    JSON,
    String
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime

from database.session import Base

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

    # Status de processamento
    processed = Column(Boolean, default=False, nullable=False)

    # Quando foi processado
    processed_at = Column(DateTime(timezone=True), nullable=True)

    # Metadados adicionais (JSON)
    capture_metadata = Column(JSON, default=dict, nullable=False)

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
    # RELACIONAMENTOS SIMPLIFICADOS
    # =========================

    user = relationship(
        "User",
        back_populates="captures"
    )

    # ⚠️ RELAÇÃO com Note COMENTADA até Note ser corrigido
    # note = relationship(
    #     "Note", 
    #     back_populates="capture",
    #     uselist=False
    # )

    # =========================
    # MÉTODOS
    # =========================

    def mark_as_processed(self):
        self.processed = True
        self.processed_at = datetime.utcnow()

    def update_summary(self, summary_text: str):
        self.summary = summary_text

    def add_metadata(self, key: str, value):
        if not self.capture_metadata:
            self.capture_metadata = {}
        self.capture_metadata[key] = value

    def __repr__(self):
        return f"<Capture(id={self.id}, source='{self.source}', processed={self.processed})>"

    def to_dict(self):
        return {
            "id": self.id,
            "raw_text": self.raw_text[:100] + "..." if len(self.raw_text) > 100 else self.raw_text,
            "summary": self.summary,
            "source": self.source,
            "user_id": self.user_id,
            "processed": self.processed,
            "processed_at": self.processed_at.isoformat() if self.processed_at else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "metadata": self.capture_metadata
        }