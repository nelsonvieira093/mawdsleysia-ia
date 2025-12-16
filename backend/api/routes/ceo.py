# backend/api/routes/ceo.py
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional, List
import os
from datetime import datetime

from backend.middleware.auth import require_any_auth

router = APIRouter(prefix="/ceo", tags=["CEO Agent"])

class CEOQuestion(BaseModel):
    question: str
    use_context: bool = True
    max_tokens: Optional[int] = 1000
    temperature: Optional[float] = 0.7

@router.post("/ask")
async def ask_ceo(
    data: CEOQuestion,
    current_user: dict = Depends(require_any_auth)
):
    """
    Faça uma pergunta para o Agente CEO
    """
    try:
        # Verificar se OpenAI está configurada
        if not os.getenv("OPENAI_API_KEY"):
            return {
                "reply": "��� **CEO Agent (Modo Demo)**\n\n"
                        f"**Pergunta:** {data.question}\n\n"
                        "Para usar a IA real, adicione OPENAI_API_KEY no arquivo .env\n"
                        "Obtenha uma chave em: https://platform.openai.com/api-keys",
                "context_used": False,
                "model": "demo",
                "timestamp": datetime.utcnow().isoformat(),
                "tokens_used": 0
            }
        
        # Tentar importar o agente CEO
        try:
            from backend.agents.ceo_agent import run_ceo_agent
            response = run_ceo_agent(data.question)
            
            return {
                "reply": response,
                "context_used": data.use_context,
                "model": "gpt-4o",
                "timestamp": datetime.utcnow().isoformat(),
                "tokens_used": len(response.split())  # Estimativa
            }
        except ImportError:
            # Se não encontrar o módulo, usar fallback
            import openai
            
            client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
            
            system_prompt = "Você é o MAWDSLEYS — Agente Executivo de Diretoria. Forneça respostas claras, diretas e profissionais."
            
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": data.question}
                ],
                max_tokens=data.max_tokens,
                temperature=data.temperature
            )
            
            ai_reply = response.choices[0].message.content
            
            return {
                "reply": ai_reply,
                "context_used": False,
                "model": response.model,
                "timestamp": datetime.utcnow().isoformat(),
                "tokens_used": response.usage.total_tokens if response.usage else 0
            }
        
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Erro no CEO Agent: {str(e)}"
        )

@router.get("/status")
async def ceo_status():
    """
    Status do CEO Agent
    """
    return {
        "status": "active" if os.getenv("OPENAI_API_KEY") else "inactive",
        "openai_configured": bool(os.getenv("OPENAI_API_KEY")),
        "agent": "MAWDSLEYS CEO Agent",
        "timestamp": datetime.utcnow().isoformat()
    }

@router.get("/test")
async def test_ceo():
    """
    Teste rápido do CEO Agent
    """
    return {
        "message": "CEO Agent está funcionando",
        "endpoint": "/api/ceo/ask",
        "method": "POST",
        "example_request": {
            "question": "Qual é a estratégia da empresa para o próximo trimestre?",
            "use_context": True
        }
    }
