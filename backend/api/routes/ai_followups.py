# backend/api/routes/ai_followups.py

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional
import os
from datetime import datetime

from ...middleware.auth import require_any_auth

# 🔹 EVENTOS / MEMÓRIA
from core.events.activity_log import ActivityEvent
from db.repositories.activity_log_repository import ActivityLogRepository
from db.session import get_db  # usa sua session padrão

router = APIRouter(prefix="/ai/followups", tags=["AI FollowUps"])


class GenerateFollowUpRequest(BaseModel):
    task: str
    responsible: str
    urgency: str = "normal"     # low, normal, high, critical
    tone: str = "professional"  # friendly, formal, urgent, diplomatic


@router.post("/generate")
async def generate_followup(
    data: GenerateFollowUpRequest,
    current_user: dict = Depends(require_any_auth),
    db=Depends(get_db)
):
    """
    Gerar follow-up automático usando IA
    + registrar memória do sistema
    """
    try:
        # ============================
        # MODO DEMO (SEM OPENAI)
        # ============================
        if not os.getenv("OPENAI_API_KEY"):
            tones = {
                "friendly": "Amigável",
                "professional": "Profissional",
                "urgent": "Urgente",
                "diplomatic": "Diplomático"
            }

            tone_desc = tones.get(data.tone, "Profissional")

            demo_response = f"""
**Follow-up Sugerido ({tone_desc})**

Para: {data.responsible}
Tarefa: {data.task}
Urgência: {data.urgency.upper()}

Prezado(a) {data.responsible},

Gostaria de acompanhar o andamento da tarefa mencionada acima.
Poderia me informar o status atual e se há algum impedimento?

Atenciosamente,
Equipe MAWDSLEYS
"""

            followup_text = demo_response.strip()
            generated_by = "demo"

        # ============================
        # IA REAL
        # ============================
        else:
            try:
                from agents.followup_agent import generate_followup as ai_generate
                followup_text = ai_generate(data.task, data.responsible)
            except ImportError:
                import openai

                client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

                system_prompt = f"""
Você é um assistente que gera follow-ups profissionais.
Tom: {data.tone}
Urgência: {data.urgency}
"""

                user_prompt = f"""
Tarefa: {data.task}
Responsável: {data.responsible}
"""

                completion = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ]
                )

                followup_text = completion.choices[0].message.content

            generated_by = "gpt-4o-mini"

        # ============================
        # 🔥 REGISTRO DE EVENTO (MEMÓRIA)
        # ============================
        event = ActivityEvent(
            type="followup.generated",
            entity="followup",
            entity_id=data.task,
            actor=current_user.get("name", "IA"),
            payload={
                "task": data.task,
                "responsible": data.responsible,
                "urgency": data.urgency,
                "tone": data.tone,
                "generated_by": generated_by
            }
        )

        repo = ActivityLogRepository(db)
        await repo.save(event)

        # ============================
        # RESPOSTA FINAL
        # ============================
        return {
            "followup": followup_text,
            "generated_by": generated_by,
            "urgency": data.urgency,
            "tone": data.tone,
            "task": data.task,
            "responsible": data.responsible,
            "timestamp": datetime.utcnow().isoformat()
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao gerar follow-up: {str(e)}"
        )


@router.get("/templates")
async def get_followup_templates():
    """
    Obter templates de followup
    """
    return {
        "templates": [
            {"name": "Acompanhamento padrão", "urgency": "normal", "tone": "professional"},
            {"name": "Lembrete urgente", "urgency": "high", "tone": "urgent"},
            {"name": "Solicitação diplomática", "urgency": "low", "tone": "diplomatic"},
            {"name": "Follow-up amigável", "urgency": "low", "tone": "friendly"}
        ]
    }
