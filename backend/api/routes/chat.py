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

# 🔹 REPOSITÓRIOS (READ ONLY)
from db.repositories.kpi_repository import KPIRepository

from models.meeting import Meeting
from models.note import Note
from models.followup import FollowUp

# 🔹 OpenAI
import openai

# =========================
# CONFIG
# =========================

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise RuntimeError("OPENAI_API_KEY não configurada")

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
        "openai": "enabled",
        "timestamp": datetime.utcnow().isoformat(),
    }

# =========================
# UTIL — DESCOBRE CAMPO USER
# =========================

def _resolve_user_field(model):
    cols = {c.key for c in inspect(model).mapper.column_attrs}
    for candidate in ("user_id", "owner_id", "created_by_id"):
        if candidate in cols:
            return getattr(model, candidate)
    raise RuntimeError(
        f"Model {model.__name__} não possui campo de usuário conhecido"
    )

# =========================
# CHAT — ACESSO TOTAL
# =========================

@router.post("", response_model=ChatResponse)
async def chat(
    data: ChatRequest,
    current_user: dict = Depends(require_any_auth),
    db: Session = Depends(get_db),
):
    user_id = current_user.get("user_id")
    user_name = current_user.get("name", "Executivo")

    if not user_id:
        raise HTTPException(status_code=401, detail="Usuário não autenticado")

    repo = ActivityLogRepository(db)

    # =========================
    # 1️⃣ FOLLOW-UPS (ENUM SAFE)
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
    # 2️⃣ KPIs
    # =========================

    kpi_repo = KPIRepository(db)
    kpi_followup = kpi_repo.followup_summary(user_id)
    kpi_perf = kpi_repo.followup_performance(user_id)
    kpi_agenda = kpi_repo.agenda_kpis(user_id)

    # =========================
    # 3️⃣ REUNIÕES
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
    # 4️⃣ NOTAS
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
    # 5️⃣ MEMÓRIA
    # =========================

    memory = MemoryEngine(db)
    try:
        memories = memory.get_user_recent_memories(user_id=user_id, limit=3)
        memory_ctx = "\n".join(m.content for m in memories)
    except Exception:
        memory_ctx = ""

    # =========================
    # 6️⃣ PROMPT EXECUTIVO
    # =========================

    system_prompt = f"""
Você é o **Agente Executivo MAWDSLEYS**.

Você possui ACESSO TOTAL aos dados reais do sistema.

📌 FOLLOW-UPS:
{chr(10).join(followups_ctx) or "Nenhum follow-up ativo."}

📊 KPIs:
- Abertos: {kpi_followup["open"]}
- Atrasados: {kpi_followup["overdue"]}
- Criados na semana: {kpi_followup["created_this_week"]}
- Fechados na semana: {kpi_followup["closed_this_week"]}
- Taxa de fechamento: {kpi_perf["closure_rate"]}%
- Prazo médio: {kpi_perf["avg_close_days"]} dias
- Vencem hoje: {kpi_agenda["due_today"]}
- Próximos 7 dias: {kpi_agenda["due_next_7_days"]}

📅 REUNIÕES:
{chr(10).join(meetings_ctx) or "Nenhuma reunião agendada."}

📝 NOTAS:
{chr(10).join(notes_ctx) or "Nenhuma nota recente."}

🧠 MEMÓRIA:
{memory_ctx or "Sem memória recente."}

REGRAS:
- NUNCA diga que não tem acesso
- Baseie respostas nos dados acima
- Seja executivo, direto e acionável

Usuário: {user_name}
"""

    # =========================
    # 7️⃣ OPENAI (COM SEGURANÇA)
    # =========================

    try:
        completion = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": data.message},
            ],
            temperature=0.3,
            request_timeout=10,
        )
        reply = completion["choices"][0]["message"]["content"]
    except Exception:
        reply = (
            "⚠️ Não consegui consultar a IA agora, "
            "mas seus dados já estão carregados.\n\n"
            f"📌 Follow-ups ativos: {len(followups)}"
        )

    # =========================
    # 8️⃣ LOG
    # =========================

    await repo.save(
        ActivityEvent(
            type="chat.executive",
            entity="chat",
            entity_id=f"chat_{datetime.utcnow().timestamp()}",
            actor=user_name,
            payload={"question": data.message[:300]},
        )
    )

    return ChatResponse(
        reply=reply,
        timestamp=datetime.utcnow().isoformat(),
    )
