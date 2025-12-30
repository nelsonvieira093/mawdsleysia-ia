# backend/api/routes/agenda.py

from fastapi import APIRouter
from controllers.agenda import build_agenda

router = APIRouter(prefix="/api", tags=["Agenda"])

@router.get("/agenda/{ritual_code}")
def get_agenda(ritual_code: str):
    return build_agenda(ritual_code)
