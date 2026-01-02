# backend/models/note_tag.py
from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship
from database.session import Base  # ⚠️ MESMO BASE DOS OUTROS MODELS

class NoteTag(Base):
    __tablename__ = "note_tags"
    
    # ID único (opcional, mas recomendado para consistência)
    id = Column(Integer, primary_key=True, index=True)
    
    # Referência à nota
    note_id = Column(
        Integer,
        ForeignKey("notes.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    
    # Referência à tag
    tag_id = Column(
        Integer,
        ForeignKey("tags.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    
    # =========================
    # RELACIONAMENTOS
    # =========================
    
    # Relação com Note
    note = relationship(
        "Note",
        back_populates="note_tags"  # Adicione no modelo Note
    )
    
    # Relação com Tag
    tag = relationship(
        "Tag",
        back_populates="note_tags"  # Adicione no modelo Tag
    )
    
    # =========================
    # MÉTODOS
    # =========================
    
    def __repr__(self):
        return f"<NoteTag(id={self.id}, note_id={self.note_id}, tag_id={self.tag_id})>"
    
    @classmethod
    def create_association(cls, note_id: int, tag_id: int):
        """Método factory para criar associação"""
        return cls(note_id=note_id, tag_id=tag_id)