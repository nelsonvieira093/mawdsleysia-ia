# backend/api/routes/__init__.py
from .import auth, followups, kpis, meetings
from .import chat  # Adicionar esta linha

__all__ = ["auth", "followups", "kpis", "meetings", "chat"]