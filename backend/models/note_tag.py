from sqlalchemy import Column, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid

from database.base import Base  # ⚠️ USAR MESMA BASE DOS OUTROS MODELOS

class NoteTag(Base):
    __tablename__ = "note_tags"
    
    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True
    )
    
    note_id = Column(
        UUID(as_uuid=True),
        ForeignKey("notes.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    
    tag_id = Column(
        UUID(as_uuid=True),
        ForeignKey("tags.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    
    # 🔁 RELACIONAMENTOS BIDIRECIONAIS CORRETOS
    note = relationship(
        "Note", 
        back_populates="note_tags",  # ⚠️ Corresponde ao back_populates no Note
        lazy="select"
    )
    
    tag = relationship(
        "Tag", 
        back_populates="note_tags",  # ⚠️ Corresponde ao back_populates no Tag
        lazy="select"
    )
    
    def __repr__(self):
        return f"<NoteTag(id={self.id}, note_id={self.note_id}, tag_id={self.tag_id})>"
    
    @classmethod
    def create_association(cls, note_id, tag_id):
        return cls(note_id=note_id, tag_id=tag_id)