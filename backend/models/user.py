# E:\MAWDSLEYS-AGENTE\backend\models\user.py

from sqlalchemy import Column, String, Boolean, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid

# Tenta importar a Base correta
try:
    from database.base import Base
except ImportError:
    # Fallback se não existir
    from sqlalchemy.ext.declarative import declarative_base
    Base = declarative_base()


class User(Base):
    __tablename__ = "users"
    __table_args__ = {'extend_existing': True}  # ✅ CRÍTICO: ADICIONE ESTA LINHA
    
    # ⚠️ MUDAR: Integer → UUID
    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True
    )

    name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    password = Column(String(255), nullable=False)

    is_active = Column(Boolean, default=True, nullable=False)
    is_admin = Column(Boolean, default=False)

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=True,
    )

    def __repr__(self) -> str:
        return f"<User id={self.id} email={self.email}>"