# backend/api/routes/ai_followups.py
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional
import os
from datetime import datetime

from backend.middleware.auth import require_any_auth

router = APIRouter(prefix="/ai/followups", tags=["AI FollowUps"])

class GenerateFollowUpRequest(BaseModel):
    task: str
    responsible: str
    urgency: str = "normal"  # low, normal, high, critical
    tone: str = "professional"  # friendly, formal, urgent, diplomatic

@router.post("/generate")
async def generate_followup(
    data: GenerateFollowUpRequest,
    current_user: dict = Depends(require_any_auth)
):
    """
    Gerar followup automático usando IA
    """
    try:
        # Modo demo se não tiver OpenAI
        if not os.getenv("OPENAI_API_KEY"):
            tones = {
                "friendly": "Amigável",
                "professional": "Profissional", 
                "urgent": "Urgente",
                "diplomatic": "Diplomático"
            }
            
            tone_desc = tones.get(data.tone, "Profissional")
            
            demo_response = f"""
��� **FollowUp Sugerido ({tone_desc})**

**Para:** {data.responsible}
**Tarefa:** {data.task}
**Urgência:** {data.urgency.upper()}

Prezado(a) {data.responsible},

Gostaria de acompanhar o andamento da tarefa mencionada acima.
Poderia me informar o status atual e se há algum impedimento?

Atenciosamente,
Equipe MAWDSLEYS

---
*Modo demo - Adicione OPENAI_API_KEY no .env para gerar com IA real*
"""
            
            return {
                "followup": demo_response.strip(),
                "generated_by": "demo",
                "urgency": data.urgency,
                "tone": data.tone,
                "task": data.task,
                "responsible": data.responsible,
                "timestamp": datetime.utcnow().isoformat()
            }
        
        # IA real
        try:
            from backend.agents.followup_agent import generate_followup as ai_generate
            response = ai_generate(data.task, data.responsible)
        except ImportError:
            # Fallback básico
            import openai
            
            client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
            
            system_prompt = f"""
Você é um assistente que gera follow-ups profissionais.
Tone: {data.tone}
Urgency: {data.urgency}
Gere um follow-up para a tarefa abaixo.
"""
            
            user_prompt = f"""
Task: {data.task}
Responsible: {data.responsible}
"""
            
            completion = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ]
            )
            
            response = completion.choices[0].message.content
        
        return {
            "followup": response,
            "generated_by": "gpt-4o-mini",
            "urgency": data.urgency,
            "tone": data.tone,
            "task": data.task,
            "responsible": data.responsible,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Erro ao gerar followup: {str(e)}"
        )

@router.get("/templates")
async def get_followup_templates():
    """
    Obter templates de followup
    """
    return {
        "templates": [
            {
                "name": "Acompanhamento padrão",
                "urgency": "normal",
                "tone": "professional"
            },
            {
                "name": "Lembrete urgente", 
                "urgency": "high",
                "tone": "urgent"
            },
            {
                "name": "Solicitação diplomática",
                "urgency": "low", 
                "tone": "diplomatic"
            },
            {
                "name": "Follow-up amigável",
                "urgency": "low",
                "tone": "friendly"
            }
        ]
    }
