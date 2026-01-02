# backend/models/user.py - VERSÃO MÍNIMA SEM RELAÇÕES
from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.sql import func
from database.session import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )

    # ⚠️ NENHUM RELACIONAMENTO - TUDO REMOVIDO
    # ⚠️ NÃO HÁ: roles, followups, captures

    def __repr__(self) -> str:
        return f"<User id={self.id} email={self.email}>"
