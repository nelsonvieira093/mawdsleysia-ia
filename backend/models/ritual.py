# backend/models/ritual.py
from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.orm import relationship

from database.session import Base  # ⬅️ IMPORTANTE: Mesma Base!

class Ritual(Base):
    __tablename__ = "rituals"

    # ⚠️ Mude UUID para Integer para compatibilidade
    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(50), unique=True, nullable=False)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    
    # ⚠️ RELAÇÕES COMENTADAS por enquanto
    # captures = relationship("Capture", back_populates="ritual")
    # notes = relationship("Note", back_populates="ritual")
    
    def __repr__(self):
        return f"<Ritual(id={self.id}, code='{self.code}', name='{self.name}')>"