# E:\MAWDSLEYS-AGENTE\backend\api\routes\chat_web.py
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from datetime import datetime
import os

# ❌ CORREÇÃO: Remova 'backend.' do import
try:
    # Tenta importar do caminho correto
    from api.middleware import require_any_auth
except ImportError:
    try:
        # Tenta importar relativo
        from ..middleware import require_any_auth
    except ImportError:
        # Fallback: função dummy se não existir
        def require_any_auth():
            return {"user_id": "system", "name": "System"}

from services.web_ai_service import run_web_chat

router = APIRouter(prefix="/chat-web", tags=["Web Chat"])


class WebChatInput(BaseModel):
    question: str


@router.post("/ask")
async def ask_web_chat(
    data: WebChatInput,
    current_user: dict = Depends(require_any_auth)
):
    if not os.getenv("OPENAI_API_KEY"):
        raise HTTPException(
            status_code=503,
            detail="OPENAI_API_KEY não configurada"
        )

    answer = run_web_chat(data.question)

    return {
        "reply": answer,
        "timestamp": datetime.utcnow().isoformat(),
        "mode": "web-chat"
    }