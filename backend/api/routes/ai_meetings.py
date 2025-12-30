# backend/api/routes/ai_meetings.py - VERSÃO CORRIGIDA
from  fastapi import APIRouter
from api.routes.auth import require_any_auth

router = APIRouter(prefix="/ai/meetings", tags=["AI Meetings"])

@router.get("/")
def ai_meetings():
    return {"message": "AI Meetings endpoint"}
    