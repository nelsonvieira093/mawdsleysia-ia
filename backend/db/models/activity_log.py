from sqlalchemy import Column, Integer, String, DateTime, JSON, text
from datetime import datetime
from db.base import Base


class ActivityLog(Base):
    __tablename__ = "activity_logs"

    id = Column(
        Integer,
        primary_key=True,
        autoincrement=True,
        server_default=text("nextval('activity_logs_id_seq')")
    )

    type = Column(String, nullable=False, index=True)
    entity = Column(String, nullable=False, index=True)
    entity_id = Column(String, nullable=False, index=True)

    user_id = Column(Integer, nullable=True, index=True)

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
        index=True,
    )

    payload = Column(JSON, nullable=True)

    action = Column(String, nullable=False)
