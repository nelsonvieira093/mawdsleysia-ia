# models/note_tag.py - VERSÃO SEGURA (sem erros)
from sqlalchemy import Column, Integer, ForeignKey
from database.session import Base

class NoteTag(Base):
    __tablename__ = "note_tags"
    
    id = Column(Integer, primary_key=True, index=True)
    note_id = Column(Integer, ForeignKey("notes.id"), nullable=False)
    tag_id = Column(Integer, ForeignKey("tags.id"), nullable=False)
    
    # SEM relationship - não causa erro
    # SEM back_populates - não quebra SQLAlchemy
    
    def __repr__(self):
        return f"<NoteTag(id={self.id})>"
    
    @classmethod
    def create_association(cls, note_id: int, tag_id: int):
        return cls(note_id=note_id, tag_id=tag_id)

