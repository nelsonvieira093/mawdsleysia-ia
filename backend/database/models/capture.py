from sqlalchemy import Column, Integer, Text, DateTime, JSON
from sqlalchemy.sql import func
from database.base import Base

class Capture(Base):
    __tablename__ = "captures"

    id = Column(Integer, primary_key=True, index=True)

    # Dani = user_id 1
    user_id = Column(Integer, nullable=False, index=True)

    # Entrada original (texto ou transcrição)
    raw_input = Column(Text, nullable=False)

    # Resultado do agente
    hashtags = Column(Text, nullable=False)
    summary = Column(Text, nullable=False)

    rituals = Column(JSON, nullable=True)
    followups = Column(JSON, nullable=True)
    directors = Column(JSON, nullable=True)

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    def __repr__(self):
        return f"<Capture id={self.id} user={self.user_id}>"
