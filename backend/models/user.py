# backend/models/user.py
from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    DateTime,
    Table,
    ForeignKey
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from database.session import Base

# ======================================================
# TABELA DE ASSOCIAÇÃO (User <-> Role)
# ======================================================

user_roles = Table(
    "user_roles",
    Base.metadata,
    Column("user_id", Integer, ForeignKey("users.id"), primary_key=True),
    Column("role_id", Integer, ForeignKey("roles.id"), primary_key=True),
)

# ======================================================
# MODEL USER
# ======================================================

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

    # ==================================================
    # RELACIONAMENTOS VÁLIDOS
    # ==================================================

    # Roles (muitos-para-muitos)
    roles = relationship(
        "Role",
        secondary=user_roles,
        back_populates="users",
        lazy="selectin",
    )

    # FollowUps
    followups = relationship(
        "FollowUp",
        back_populates="user",
        cascade="all, delete-orphan",
    )

    # Captures
    captures = relationship(
        "Capture",
        back_populates="user",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<User id={self.id} email={self.email}>"