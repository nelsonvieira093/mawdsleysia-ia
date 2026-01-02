# backend/models/user.py
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Table, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database.session import Base

# Tabela de associação muitos-para-muitos para User-Role
user_roles = Table(
    'user_roles',
    Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id'), primary_key=True),
    Column('role_id', Integer, ForeignKey('roles.id'), primary_key=True)
)

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)  # Flag simples
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # =========================
    # RELACIONAMENTOS
    # =========================
    
    # 1. Roles (muitos-para-muitos)
    roles = relationship(
        "Role",
        secondary=user_roles,
        back_populates="users"
    )
    
    # 2. Followups (um-para-muitos) - NOTE: "FollowUp" com U maiúsculo
    followups = relationship(
        "FollowUp",
        back_populates="user",
        cascade="all, delete-orphan"
    )
    
    # 3. Captures (um-para-muitos)
    captures = relationship(
        "Capture",
        back_populates="user",
        cascade="all, delete-orphan"
    )
    
    # 4. Notes (através de Capture)
    # notes = relationship("Note", back_populates="user")  # Se existir
    
    # 5. Activity Logs
    activity_logs = relationship(
        "ActivityLog",
        back_populates="user",
        cascade="all, delete-orphan"
    )
    
    def __repr__(self):
        return f"<User(id={self.id}, email='{self.email}')>"