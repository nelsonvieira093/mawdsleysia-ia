# backend/models/role.py - VERSÃO MÍNIMA
from sqlalchemy import Column, Integer, String, Text
from database.session import Base

class Role(Base):
    __tablename__ = "roles"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False)
    description = Column(Text)
    
    # ⚠️ SEM RELACIONAMENTO com users
    # ⚠️ users = relationship(...) REMOVIDO
    
    def __repr__(self):
        return f"<Role(id={self.id}, name={self.name})>"
