# backend/api/routes/ceo.py

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional
import os
from datetime import datetime

from backend.api.middleware import require_any_auth

router = APIRouter(prefix="/ceo", tags=["CEO Agent"])

# =========================================================
# MODELOS DE ENTRADA
# =========================================================

class CEOQuestion(BaseModel):
    """
    MODELO LEGADO (CHAT)
    """
    question: str
    use_context: bool = True
    max_tokens: Optional[int] = 1000
    temperature: Optional[float] = 0.7


class CEOCaptureInput(BaseModel):
    """
    MODELO EXECUTIVO (BULLET JOURNAL)
    Texto ou áudio transcrito da CEO
    """
    input: str


# =========================================================
# ENDPOINT LEGADO — CHAT EXECUTIVO (MANTIDO)
# =========================================================

@router.post("/ask")
async def ask_ceo(
    data: CEOQuestion,
    current_user: dict = Depends(require_any_auth)
):
    """
    Chat executivo genérico (LEGADO).
    NÃO é o produto principal da Dani.
    """
    try:
        if not os.getenv("OPENAI_API_KEY"):
            return {
                "reply": (
                    "⚠️ CEO Agent em modo DEMO.\n\n"
                    f"Pergunta: {data.question}\n\n"
                    "Configure OPENAI_API_KEY no .env para usar IA real."
                ),
                "model": "demo",
                "timestamp": datetime.utcnow().isoformat()
            }

        try:
            from agents.ceo_agent import run_ceo_agent
            response = run_ceo_agent(data.question)

            return {
                "reply": response,
                "model": "gpt-4o",
                "timestamp": datetime.utcnow().isoformat(),
                "tokens_used": len(response.split())
            }

        except ImportError:
            import openai
            openai.api_key = os.getenv("OPENAI_API_KEY")

            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "Você é o MAWDSLEYS — Assistente Executivo. "
                            "Responda de forma clara, objetiva e profissional."
                        )
                    },
                    {"role": "user", "content": data.question}
                ],
                max_tokens=data.max_tokens,
                temperature=data.temperature
            )

            return {
                "reply": response.choices[0].message.content,
                "model": response.model,
                "timestamp": datetime.utcnow().isoformat(),
                "tokens_used": response.usage.total_tokens if response.usage else 0
            }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro no CEO Agent (ask): {str(e)}"
        )


# =========================================================
# ENDPOINT PRINCIPAL — AGENTE EXECUTIVO (PRODUTO DA DANI)
# =========================================================

@router.post("/capture")
async def capture_ceo_thought(
    data: CEOCaptureInput,
    current_user: dict = Depends(require_any_auth)
):
    """
    Registro de pensamento executivo da CEO.
    NÃO é chat.
    Cada chamada gera UM capture com memória persistente.
    """
    try:
        if not os.getenv("OPENAI_API_KEY"):
            raise HTTPException(
                status_code=503,
                detail="OPENAI_API_KEY não configurada"
            )

        from agents.ceo_agent import CEOAgent
        from database.session import SessionLocal
        from models.capture import Capture

        agent = CEOAgent(user_id=current_user["id"])
        structured = agent.process_capture(data.input)

        db = SessionLocal()

        capture = Capture(
            user_id=current_user["id"],
            raw_input=data.input,
            structured_summary=structured,
            hashtags=structured.get("hashtags", []),
            rituals=structured.get("rituals"),
            directors=structured.get("directors"),
            followups=structured.get("followups"),
            confidence_level=structured.get("confidence_level"),
        )

        db.add(capture)
        db.commit()

        return {
            "status": "captured",
            "data": structured,
            "timestamp": datetime.utcnow().isoformat()
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao registrar pensamento executivo: {str(e)}"
        )


# =========================================================
# STATUS / SAÚDE
# =========================================================

@router.get("/status")
async def ceo_status():
    return {
        "agent": "MAWDSLEYS — Agente Executivo",
        "openai_configured": bool(os.getenv("OPENAI_API_KEY")),
        "status": "active" if os.getenv("OPENAI_API_KEY") else "inactive",
        "timestamp": datetime.utcnow().isoformat()
    }


@router.get("/test")
async def test_ceo():
    return {
        "message": "CEO Agent ativo",
        "main_endpoint": "/api/ceo/capture",
        "legacy_endpoint": "/api/ceo/ask",
        "method": "POST",
        "example_capture_request": {
            "input": "Falei com o time comercial e precisamos rever metas do próximo mês."
        }
    }
