#e/MAWDSLEYS-AGENTE/backend/models/kpi.py 

from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Text, JSON, ForeignKey
from sqlalchemy.sql import func
from database.base import Base


class KPI(Base):
    __tablename__ = "kpis"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False, index=True)
    description = Column(Text, nullable=True)
    target_value = Column(Float, nullable=False)
    current_value = Column(Float, default=0.0)
    unit = Column(String(50), default="")
    frequency = Column(String(50), default="monthly")
    department = Column(String(100), nullable=True)
    category = Column(String(100), nullable=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    metadata = Column(JSON, nullable=True, default=dict)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def __repr__(self):
        return f"<KPI(id={self.id}, name='{self.name}', value={self.current_value}/{self.target_value})>"
    
    @property
    def progress_percentage(self):
        """Calcula o percentual de progresso"""
        if self.target_value == 0:
            return 0
        return (self.current_value / self.target_value) * 100
    
    @property
    def status(self):
        """Determina o status baseado no progresso"""
        progress = self.progress_percentage
        
        if progress >= 90:
            return "on_track"
        elif progress >= 70:
            return "at_risk"
        else:
            return "off_track"
