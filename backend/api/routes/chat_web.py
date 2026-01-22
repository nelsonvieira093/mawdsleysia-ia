from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from datetime import datetime
import os

from backend.api.middleware import require_any_auth
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
