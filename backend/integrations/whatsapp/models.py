# backend/integrations/whatsapp/models.py

from  sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey
from  sqlalchemy.orm import relationship
from  datetime import datetime

# IMPORTAÇÃO CORRETA DO BASE
from database.session import Base


class Conversation(Base):
    __tablename__ = "wa_conversations"

    id = Column(Integer, primary_key=True, index=True)
    external_id = Column(String, unique=True, index=True, nullable=False)  # ID do provedor / telefone
    name = Column(String, nullable=True)
    last_message = Column(Text, nullable=True)
    unread = Column(Boolean, default=False)
    updated_at = Column(DateTime, default=datetime.utcnow)

    messages = relationship(
        "WAmessage",
        back_populates="conversation",
        cascade="all, delete-orphan"
    )


class WAmessage(Base):
    __tablename__ = "wa_messages"

    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(Integer, ForeignKey("wa_conversations.id"), nullable=False)
    external_id = Column(String, nullable=True)  # ID no provedor
    direction = Column(String, nullable=False)  # "in" ou "out"
    text = Column(Text, nullable=True)
    media_url = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    status = Column(String, default="received")  # delivered, failed, read, sent

    conversation = relationship("Conversation", back_populates="messages")
