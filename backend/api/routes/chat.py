import os
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import inspect

from database.session import get_db
from api.routes.auth import require_any_auth

# 🔹 EVENTOS
from core.events.activity_log import ActivityEvent
from db.repositories.activity_log_repository import ActivityLogRepository
from core.memory.memory_engine import MemoryEngine

# 🔹 REPOSITÓRIOS
from db.repositories.kpi_repository import KPIRepository

from models.meeting import Meeting
from models.note import Note
from database.db_models import FollowUp

# 🔹 OPENAI SDK ESTÁVEL (PRODUÇÃO)
import openai

# =========================
# CONFIG
# =========================

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# ⚠️ NÃO derruba a aplicação se a chave faltar
if OPENAI_API_KEY:
    openai.api_key = OPENAI_API_KEY

router = APIRouter(prefix="/api/v1/chat", tags=["Chat MAWDSLEYS"])

# =========================
# SCHEMAS
# =========================

class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    reply: str
    timestamp: str

# =========================
# HEALTH
# =========================

@router.get("/health")
def chat_health():
    return {
        "status": "online",
        "service": "MAWDSLEYS Chat",
        "openai_configured": bool(OPENAI_API_KEY),
        "timestamp": datetime.utcnow().isoformat(),
    }

# =========================
# UTIL
# =========================

def _resolve_user_field(model):
    cols = {c.key for c in inspect(model).mapper.column_attrs}
    for candidate in ("user_id", "owner_id", "created_by_id"):
        if candidate in cols:
            return getattr(model, candidate)
    raise RuntimeError(f"Model {model.__name__} não possui campo de usuário conhecido")

# =========================
# CHAT
# =========================

@router.post("", response_model=ChatResponse)
async def chat(
    data: ChatRequest,
    current_user: dict = Depends(require_any_auth),
    db: Session = Depends(get_db),
):
    user_id = current_user.get("user_id")
    user_name = current_user.get("email", "Executivo")

    if not user_id:
        raise HTTPException(status_code=401, detail="Usuário não autenticado")

    repo = ActivityLogRepository(db)

    # =========================
    # FOLLOW-UPS
    # =========================

    user_field = _resolve_user_field(FollowUp)

    followups = (
        db.query(FollowUp)
        .filter(user_field == user_id)
        .filter(FollowUp.status.in_(("ABERTO", "EM_ANDAMENTO")))
        .order_by(FollowUp.created_at.desc())
        .limit(10)
        .all()
    )

    followups_ctx = [
        f"- {f.description} | prioridade={f.priority} | status={f.status}"
        for f in followups
    ]

    # =========================
    # KPIs
    # =========================

    kpi_repo = KPIRepository(db)
    kpi_followup = kpi_repo.followup_summary(user_id)
    kpi_perf = kpi_repo.followup_performance(user_id)
    kpi_agenda = kpi_repo.agenda_kpis(user_id)

    # =========================
    # REUNIÕES
    # =========================

    meetings = (
        db.query(Meeting)
        .filter(Meeting.organizer_id == user_id)
        .order_by(Meeting.scheduled_time.asc())
        .limit(5)
        .all()
    )

    meetings_ctx = [
        f"- {m.title} em {m.scheduled_time.strftime('%d/%m %H:%M')} | {m.status}"
        for m in meetings
    ]

    # =========================
    # NOTAS
    # =========================

    notes = (
        db.query(Note)
        .filter(Note.user_id == user_id)
        .order_by(Note.created_at.desc())
        .limit(5)
        .all()
    )

    notes_ctx = [
        f"- {n.title or 'Sem título'} | status={n.status}"
        for n in notes
    ]

    # =========================
    # MEMÓRIA
    # =========================

    memory_ctx = ""
    try:
        memory = MemoryEngine(db)
        memories = memory.get_user_recent_memories(user_id=user_id, limit=3)
        memory_ctx = "\n".join(m.content for m in memories)
    except Exception:
        pass

    # =========================
    # PROMPT
    # =========================

    system_prompt = f"""
Você é o Agente Executivo MAWDSLEYS.

FOLLOW-UPS:
{chr(10).join(followups_ctx) or "Nenhum follow-up ativo."}

KPIs:
- Abertos: {kpi_followup.get("open")}
- Atrasados: {kpi_followup.get("overdue")}

REUNIÕES:
{chr(10).join(meetings_ctx) or "Nenhuma reunião."}

NOTAS:
{chr(10).join(notes_ctx) or "Nenhuma nota."}

MEMÓRIA:
{memory_ctx or "Sem memória recente."}

Usuário: {user_name}
"""

    # =========================
    # OPENAI (ESTÁVEL)
    # =========================

    reply = "⚠️ IA indisponível no momento, mas seus dados estão carregados."

    if OPENAI_API_KEY:
        try:
            completion = openai.ChatCompletion.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": data.message},
                ],
                temperature=0.3,
            )
            reply = completion.choices[0].message["content"]
        except Exception:
            pass

    # =========================
    # LOG (NÃO QUEBRA CHAT)
    # =========================

    try:
        await repo.save(
            ActivityEvent(
                type="chat.executive",
                entity="chat",
                entity_id=f"chat_{datetime.utcnow().timestamp()}",
                actor=user_name,
                payload={"question": data.message[:300]},
            )
        )
    except Exception:
        pass

    return ChatResponse(
        reply=reply,
        timestamp=datetime.utcnow().isoformat(),
    )
