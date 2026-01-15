# backend/models/wa_message.py
from  sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, ForeignKey, Enum
from  sqlalchemy.orm import relationship
from  sqlalchemy.sql import func
import enum
from database.session import Base

class MessageType(enum.Enum):
    TEXT = "text"
    IMAGE = "image"
    AUDIO = "audio"
    VIDEO = "video"
    DOCUMENT = "document"
    LOCATION = "location"
    CONTACT = "contact"
    STICKER = "sticker"

class MessageStatus(enum.Enum):
    SENT = "sent"
    DELIVERED = "delivered"
    READ = "read"
    FAILED = "failed"

class WAMessage(Base):
    __tablename__ = "wa_messages"
    
    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(Integer, ForeignKey('wa_conversations.id', ondelete='CASCADE'), nullable=False)
    message_id = Column(String(255), unique=True, nullable=False)  # ID único do WhatsApp
    from_me = Column(Boolean, default=False)  # True se foi enviada por mim
    sender_number = Column(String(20))
    sender_name = Column(String(255))
    message_type = Column(Enum(MessageType), default=MessageType.TEXT)
    content = Column(Text)
    media_url = Column(String(500))  # URL para mídia
    file_name = Column(String(255))
    file_size = Column(Integer)  # Em bytes
    timestamp = Column(DateTime(timezone=True), nullable=False)
    status = Column(Enum(MessageStatus), default=MessageStatus.SENT)
    read_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relacionamento
    conversation = relationship("WAConversation", back_populates="messages")
    
    def __repr__(self):
        return f"<WAMessage(id={self.id}, type={self.message_type}, from_me={self.from_me})>"