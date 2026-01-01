# backend/models/followup.py
from sqlalchemy import (
    Column,
    Integer,
    Text,
    Date,
    Enum,
    ForeignKey,
    DateTime,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from database.session import Base  # ✅ MESMO BASE DO USER

# =========================
# FOLLOWUP MODEL
# =========================
class FollowUp(Base):
    __tablename__ = "followups"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    description = Column(Text, nullable=False)

    due_date = Column(Date)

    status = Column(
        Enum(
            "ABERTO",
            "EM_ANDAMENTO",
            "CONCLUIDO",
            name="followup_status",
        ),
        default="ABERTO",
        nullable=False,
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    # =========================
    # RELACIONAMENTOS
    # =========================
    user = relationship(
        "User",
        back_populates="followups",
    )

    def __repr__(self):
        return f"<FollowUp id={self.id} user_id={self.user_id}>"
