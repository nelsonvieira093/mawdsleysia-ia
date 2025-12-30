#E:\MAWDSLEYS-AGENTE\backend\models\note_tag.py
from sqlalchemy import Column, ForeignKey
from sqlalchemy.dialects.postgresql import UUID

from database.base import Base


class NoteTag(Base):
    __tablename__ = "note_tags"

    note_id = Column(
        UUID(as_uuid=True),
        ForeignKey("notes.id", ondelete="CASCADE"),
        primary_key=True,
    )

    tag_id = Column(
        UUID(as_uuid=True),
        ForeignKey("tags.id", ondelete="CASCADE"),
        primary_key=True,
    )
