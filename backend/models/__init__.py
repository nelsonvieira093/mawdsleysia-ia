# backend/models/__init__.py - APENAS USER E ROLE
from database.session import Base

# 1. Role primeiro (não depende de ninguém)
from .role import Role

# 2. User depois (agora não depende de Role para relações)
from .user import User

# ⚠️ NÃO IMPORTE MAIS NADA
# from .followup import FollowUp
# from .capture import Capture
# from .note import Note
# from .note_tag import NoteTag
# from .ritual import Ritual
# from .person import Person

__all__ = [
    "Base",
    "Role",  # Sem relações
    "User",  # Sem relações
]
