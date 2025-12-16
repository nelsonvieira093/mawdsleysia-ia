# backend/models/wa_conversation.py
from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from backend.database.session import Base

class WAConversation(Base):
    __tablename__ = "wa_conversations"
    
    id = Column(Integer, primary_key=True, index=True)
    phone_number = Column(String(20), nullable=False, index=True)
    contact_name = Column(String(255))
    is_group = Column(Boolean, default=False)
    group_name = Column(String(255))
    last_message_at = Column(DateTime(timezone=True))
    unread_count = Column(Integer, default=0)
    is_archived = Column(Boolean, default=False)
    is_muted = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relacionamento com mensagens
    messages = relationship("WAMessage", back_populates="conversation", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<WAConversation(id={self.id}, phone={self.phone_number})>"