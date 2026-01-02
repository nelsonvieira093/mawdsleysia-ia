# backend/models/__init__.py
from database.session import Base

# Importe APENAS os models que você DEFINITIVAMENTE TEM E USA
from .user import User
from .role import Role
from .followup import FollowUp
from .capture import Capture
from .note import Note
from .note_tag import NoteTag
from .ritual import Ritual
from .person import Person

# NÃO importe models que não existem ou não usa
# REMOVA estas linhas se os arquivos não existirem:
# from .activity_log import ActivityLog
# from .decision import Decision  
# from .setting import Setting
# from .tag import Tag

__all__ = [
    "Base",
    "User",
    "Role",
    "FollowUp",
    "Capture",
    "Note",
    "NoteTag",
    "Ritual",
    "Person",
]