# backend/database/models.py - VERSÃO CORRIGIDA
from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime

from session import Base

# ⚠️ REMOVER a classe User daqui - Ela já existe em backend/models/user.py
# class User(Base):  # COMENTE OU REMOVA ESTA CLASSE
#     __tablename__ = "users"
#     ... todo o conteúdo ...

class FollowUp(Base):
    __tablename__ = "followups"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    message = Column(Text, nullable=False)
    resolved = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    user_id = Column(Integer, ForeignKey("users.id"))  # 🔗 Refere-se à tabela users REAL
    user = relationship("User", back_populates="followups")


class KPI(Base):
    __tablename__ = "kpis"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(Text)
    progress = Column(Integer, default=0)  # 0–100%
    deadline = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)

    user_id = Column(Integer, ForeignKey("users.id"))
    user = relationship("User", back_populates="kpis")


class Meeting(Base):
    __tablename__ = "meetings"

    id = Column(Integer, primary_key=True, index=True)
    topic = Column(String, nullable=False)
    scheduled_for = Column(DateTime, nullable=False)
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

    user_id = Column(Integer, ForeignKey("users.id"))
    user = relationship("User", back_populates="meetings")