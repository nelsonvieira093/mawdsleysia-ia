# backend/models/role.py - COM extend_existing
from  sqlalchemy import Column, Integer, String, Text
from  sqlalchemy.orm import relationship
from  database.session import Base

class Role(Base):
    __tablename__ = "roles"
    __table_args__ = {'extend_existing': True}  # ⬅️ ADICIONE
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False)
    description = Column(Text)
    
    users = relationship("User", secondary="user_roles", back_populates="roles")
    
    def __repr__(self):
        return f"<Role(id={self.id}, name={self.name})>"
