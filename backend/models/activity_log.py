# backend/models/activity_log.py
from  sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from  sqlalchemy.orm import relationship
from  sqlalchemy.sql import func
from  database.session import Base

class ActivityLog(Base):
    __tablename__ = "activity_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    action = Column(String(255), nullable=False)
    details = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    user = relationship("User", back_populates="activity_logs")
    
    def __repr__(self):
        return f"<ActivityLog(id={self.id}, action={self.action}, user_id={self.user_id})>"