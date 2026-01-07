# E:\MAWDSLEYS-AGENTE\backend\api\routes\chat.py — PRODUÇÃO (SEM DEMO)

import os
from datetime import datetime
from typing import List, Optional
import hashlib

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from database.session import get_db
from api.routes.auth import require_any_auth

# 🔹 EVENTOS / MEMÓRIA / ORQUESTRAÇÃO
from core.events.activity_log import ActivityEvent
from db.repositories.activity_log_repository import ActivityLogRepository
from core.memory.memory_engine import MemoryEngine

# 🔹 OpenAI
from openai import OpenAI

# =========================
# CONFIG
# =========================

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise RuntimeError("OPENAI_API_KEY não configurada no ambiente")

client = OpenAI(api_key=OPENAI_API_KEY)

router = APIRouter(prefix="/api/v1/chat", tags=["Chat MAWDSLEYS"])

# =========================
# SCHEMAS
# =========================

class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    reply: str
    context_used: Optional[List[str]] = None
    suggestions: Optional[List[str]] = None
    timestamp: str

# =========================
# HEALTH
# =========================

@router.get("/health")
def chat_health():
    return {
        "status": "online",
        "service": "MAWDSLEYS Chat",
        "openai": "enabled",
        "timestamp": datetime.utcnow().isoformat()
    }

# =========================
# UTIL FUNCTIONS
# =========================

def _generate_suggestions(user_message: str) -> List[str]:
    """Gera sugestões com base na mensagem do usuário"""
    suggestions = []
    message_lower = user_message.lower()
    
    # Sugestões baseadas no conteúdo da mensagem
    if any(word in message_lower for word in ["reunião", "meeting", "agenda", "encontro"]):
        suggestions.extend([
            "📅 Criar nova reunião",
            "👥 Ver participantes",
            "⏰ Agendar follow-up"
        ])
    
    if any(word in message_lower for word in ["tarefa", "task", "fazer", "pendente"]):
        suggestions.extend([
            "✅ Criar nova tarefa",
            "📋 Listar pendências",
            "🎯 Definir prioridades"
        ])
    
    if any(word in message_lower for word in ["relatório", "resumo", "estatística", "métrica"]):
        suggestions.extend([
            "📊 Gerar relatório de reuniões",
            "📈 Ver métricas da semana",
            "🎪 Resumo de atividades"
        ])
    
    return suggestions[:3] if suggestions else ["📅 Agendar reunião", "✅ Criar tarefa", "📊 Ver relatórios"]

def _log_chat_event_safe(db: Session, user_id: str, user_message: str, ai_response: str):
    """Registra evento de chat de forma segura"""
    try:
        repo = ActivityLogRepository(db)
        event = ActivityEvent(
            type="chat.interaction",
            entity="chat",
            entity_id=f"chat_{datetime.utcnow().timestamp()}",
            actor=str(user_id),
            payload={
                "user_message": user_message[:500],  # Limita tamanho
                "ai_response_length": len(ai_response),
                "timestamp": datetime.utcnow().isoformat()
            }
        )
        import asyncio
        asyncio.create_task(repo.save(event))
    except Exception as e:
        print(f"[Chat] Erro ao registrar evento: {e}")

# =========================
# CHAT COM MEMÓRIA REAL E INTELIGENTE
# =========================

@router.post("", response_model=ChatResponse)
async def chat(
    data: ChatRequest,
    current_user: dict = Depends(require_any_auth),
    db: Session = Depends(get_db),
):
    try:
        user_id = current_user.get("user_id")
        user_name = current_user.get("name", "Executivo")
        
        if not user_id:
            raise HTTPException(status_code=401, detail="Usuário não autenticado")

        repo = ActivityLogRepository(db)

        # =========================
        # 1️⃣ CONSULTA MEMÓRIA (INTELIGENTE) - ANTES DE RESPONDER
        # =========================
        memory = MemoryEngine(db)
        
        # Busca contexto relevante na memória
        context_memories = memory.search(
            query=data.message,
            user_id=user_id,
            limit=5,
            entity_types=["meeting", "follow_up", "task", "alert", "chat_interaction"]
        )
        
        # Busca histórico recente do usuário
        user_history = memory.get_user_recent_memories(
            user_id=user_id,
            limit=3
        )
        
        # Constrói contexto para a IA
        context_parts = []
        context_ids = []
        
        for mem in context_memories:
            context_parts.append(f"[{mem.entity_type.upper()}] {mem.content}")
            context_ids.append(str(mem.id))
        
        for mem in user_history:
            if str(mem.id) not in context_ids:
                context_parts.append(f"[HISTÓRICO] {mem.content}")
                context_ids.append(str(mem.id))
        
        memory_context = "\n".join(context_parts) if context_parts else "Sem contexto prévio relevante."
        
        # 🔹 Log de consulta à memória (explicabilidade)
        memory_event = ActivityEvent(
            type="memory.consulted",
            entity="memory",
            entity_id="chat_context",
            actor="MAWDSLEYS_AI",
            payload={
                "events_loaded": len(context_memories) + len(user_history),
                "context_ids": context_ids[:5],  # Apenas os primeiros IDs
                "query": data.message[:100]
            }
        )
        await repo.save(memory_event)

        # =========================
        # 2️⃣ LOG MENSAGEM DO USUÁRIO
        # =========================
        user_event = ActivityEvent(
            type="chat.user_message",
            entity="chat",
            entity_id="conversation",
            actor=user_name,
            payload={
                "message": data.message,
                "user_id": user_id
            }
        )
        await repo.save(user_event)

        # =========================
        # 3️⃣ PROMPT EXECUTIVO COM CONTEXTO INTELIGENTE
        # =========================
        system_prompt = f"""
Você é o Agente Executivo MAWDSLEYS.

Você tem acesso ao histórico REAL da empresa e memória do usuário.
Use o contexto abaixo para responder de forma relevante.

=== MEMÓRIA E CONTEXTO DO USUÁRIO ===
{memory_context}

=== REGRAS DO AGENTE MAWDSLEYS ===
1. Seja objetivo e executivo
2. Baseie respostas nos fatos do histórico quando disponível
3. Se algo não existir no histórico, seja transparente
4. Ofereça sugestões úteis quando apropriado
5. Formate respostas de forma clara e profissional
6. Use emojis relevantes para melhorar a legibilidade

Usuário: {user_name} (ID: {user_id})
"""

        # =========================
        # 4️⃣ OPENAI COM CONTEXTO ENRIQUECIDO
        # =========================
        completion = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": data.message}
            ],
            temperature=0.3
        )

        reply_text = completion.choices[0].message.content

        # =========================
        # 5️⃣ REGISTRA INTERAÇÃO NA MEMÓRIA DO AGENTE
        # =========================
        memory_content = f"Usuário {user_name} perguntou: '{data.message}'. IA respondeu: '{reply_text[:100]}...'"
        
        memory.add_memory(
            user_id=user_id,
            entity_type="chat_interaction",
            entity_id=f"chat_{datetime.utcnow().timestamp()}",
            content=memory_content,
            metadata={
                "user_message": data.message,
                "ai_response": reply_text,
                "context_used": context_ids,
                "timestamp": datetime.utcnow().isoformat()
            }
        )

        # =========================
        # 6️⃣ LOG RESPOSTA DA IA
        # =========================
        ai_event = ActivityEvent(
            type="chat.ai_response",
            entity="chat",
            entity_id="conversation",
            actor="MAWDSLEYS_AI",
            payload={
                "reply_preview": reply_text[:200] + "..." if len(reply_text) > 200 else reply_text,
                "model": "gpt-4o-mini",
                "context_used_count": len(context_ids)
            }
        )
        await repo.save(ai_event)

        # =========================
        # 7️⃣ REGISTRA EVENTO DE CHAT (BACKUP)
        # =========================
        _log_chat_event_safe(db, user_id, data.message, reply_text)

        # =========================
        # 8️⃣ GERA SUGESTÕES INTELIGENTES
        # =========================
        suggestions = _generate_suggestions(data.message)

        # =========================
        # 9️⃣ RESPOSTA COMPLETA
        # =========================
        return ChatResponse(
            reply=reply_text,
            context_used=context_ids[:3] if context_ids else None,
            suggestions=suggestions,
            timestamp=datetime.utcnow().isoformat()
        )

    except HTTPException:
        raise
    except Exception as e:
        # Log do erro
        print(f"[Chat Error] {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Erro no Chat MAWDSLEYS: {str(e)}"
        )

# =========================
# CHAT SIMPLES (FALLBACK)
# =========================

@router.post("/simple")
async def chat_simple(
    data: ChatRequest,
    current_user: dict = Depends(require_any_auth),
):
    """Chat simplificado sem consulta de memória (fallback)"""
    try:
        completion = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Você é o assistente corporativo MAWDSLEYS. Responda de forma profissional e útil."},
                {"role": "user", "content": data.message}
            ],
            temperature=0.3
        )
        
        reply_text = completion.choices[0].message.content
        
        return ChatResponse(
            reply=reply_text,
            timestamp=datetime.utcnow().isoformat()
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro no chat simplificado: {str(e)}"
        )

# =========================
# CHAT PUBLIC (PARA TESTES)
# =========================

@router.post("/public", response_model=ChatResponse)
async def chat_public(
    data: ChatRequest,
    db: Session = Depends(get_db)
):
    """Chat público para testes (sem autenticação)"""
    try:
        user_id = "test_user"
        user_name = "Test User"
        
        # Versão simplificada para teste:
        completion = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Você é o assistente corporativo MAWDSLEYS. Responda de forma profissional."},
                {"role": "user", "content": data.message}
            ],
            temperature=0.3
        )
        
        reply_text = completion.choices[0].message.content
        
        # Registra evento do chat público (opcional)
        try:
            repo = ActivityLogRepository(db)
            event = ActivityEvent(
                type="chat.public_message",
                entity="chat",
                entity_id=f"public_chat_{datetime.utcnow().timestamp()}",
                actor=user_id,
                payload={
                    "message": data.message,
                    "reply_preview": reply_text[:100] + "..." if len(reply_text) > 100 else reply_text,
                    "timestamp": datetime.utcnow().isoformat()
                }
            )
            await repo.save(event)
        except Exception as e:
            print(f"[Chat Public] Erro ao registrar evento: {e}")
        
        return ChatResponse(
            reply=reply_text,
            timestamp=datetime.utcnow().isoformat()
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro no chat público: {str(e)}"
        )