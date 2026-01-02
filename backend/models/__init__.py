# backend/models/__init__.py
from database.session import Base

# IMPORTE EM ORDEM CORRETA: base primeiro, depois dependências
from .ritual import Ritual  # ⬅️ PRIMEIRO: Não depende de ninguém
from .role import Role      # ⬅️ Não depende de ninguém
from .person import Person  # ⬅️ Se existir, coloque cedo
from .user import User      # ⬅️ DEPENDE de Role (já importado)
from .capture import Capture # ⬅️ DEPENDE de User (já importado)
from .note import Note       # ⬅️ DEPENDE de Capture, User, Ritual
from .note_tag import NoteTag # ⬅️ DEPENDE de Note
from .followup import FollowUp # ⬅️ DEPENDE de User, Note

# NÃO importe models que não existem
# REMOVA estas linhas se os arquivos não existirem:
# from .activity_log import ActivityLog
# from .decision import Decision  
# from .setting import Setting
# from .tag import Tag  # ⬅️ SE Tiver model Tag, precisa criar

__all__ = [
    "Base",
    "Ritual",
    "Role",
    "Person",
    "User",
    "Capture",
    "Note",
    "NoteTag",
    "FollowUp",
]