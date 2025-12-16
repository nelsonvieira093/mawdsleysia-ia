# backend/models/user.py - VERSÃO COM STRINGS
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Table, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from backend.database.session import Base

# Tabela de associação
user_role = Table(
    'user_roles',
    Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id', ondelete='CASCADE'), primary_key=True),
    Column('role_id', Integer, ForeignKey('roles.id', ondelete='CASCADE'), primary_key=True),
    extend_existing=True
)

class User(Base):
    __tablename__ = "users"
    __table_args__ = {'extend_existing': True}

    # Colunas principais
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relacionamentos com tabelas antigas - USE STRINGS
    followups = relationship(
        "FollowUp",  # ⬅️ String, não classe
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="dynamic"
    )
    
    kpis = relationship(
        "KPI",  # ⬅️ String
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="dynamic"
    )
    
    meetings = relationship(
        "Meeting",  # ⬅️ String
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="dynamic"
    )
    
    # Relacionamentos com tabelas novas
    roles = relationship(
        "Role",  # ⬅️ String
        secondary=user_role, 
        back_populates="users",
        lazy="selectin"
    )
    
    sessions = relationship(
        "Session",  # ⬅️ String
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="dynamic"
    )
    
    activity_logs = relationship(
        "ActivityLog",  # ⬅️ String
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="dynamic"
    )
    
    def __repr__(self):
        return f"<User(id={self.id}, email={self.email}, name={self.name})>"
