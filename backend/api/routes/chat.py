# backend/api/routes/chat.py - VERSÃO CORRIGIDA
from fastapi import APIRouter

router = APIRouter(prefix="/chat", tags=["Chat"])

@router.get("/")
def chat():
    return {"message": "Chat endpoint"}
