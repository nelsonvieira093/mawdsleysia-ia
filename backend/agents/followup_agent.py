# E:\MAWDSLEYS-AGENTE\backend\agents\followup_agent.py

from datetime import datetime
from sqlalchemy.orm import Session
import openai  # ✅ CORRIGIDO

from core.memory.memory_engine import MemoryEngine
from core.events.activity_log import ActivityEvent
from db.repositories.activity_log_repository import ActivityLogRepository

# ✅ CORRETO:
from database.db_models import FollowUp
from schemas.followup import FollowUpOut, FollowUpStatus


class FollowUpAgent:
    def __init__(self, db: Session):
        self.db = db
        self.memory = MemoryEngine(db)
        self.repo = ActivityLogRepository(db)

    async def generate_followup(self, task: str, responsible: str, user_id: int):
        """
        Gera follow-up profissional baseado na memória real do MAWDSLEYS
        """

        # 🔍 Busca contexto real no histórico do sistema
        memories = self.memory.search(
            query=task,
            user_id=user_id,
            limit=5,
            entity_types=["meeting", "task", "followup", "alert"]
        )

        context = "\n".join(
            f"- {m.content}" for m in memories
        ) if memories else "Nenhum contexto relacionado encontrado."

        # ✅ SEU SYSTEM PROMPT (PRESERVADO)
        system_prompt = f"""
Você é o MAWDSLEYS — Agente Especialista em Follow-Ups.

Sua missão:
- Criar follow-ups profissionais
- Linguagem executiva
- Objetivo e direto
- Pressão sem ser agressivo
- Incluir datas quando possível

Contexto relacionado:
{context}
"""

        user_prompt = f"""
Crie um follow-up para:

Tarefa: {task}
Responsável: {responsible}
"""

        completion = openai.ChatCompletion.create(  # ✅ CORRIGIDO
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.3
        )

        followup_text = completion.choices[0].message.content

        # 🧾 Auditoria / rastreabilidade
        event = ActivityEvent(
            type="followup.generated",
            entity="followup",
            entity_id=f"followup_{datetime.utcnow().timestamp()}",
            actor=f"user_{user_id}",
            payload={
                "task": task,
                "responsible": responsible,
                "content": followup_text,
                "generated_at": datetime.utcnow().isoformat()
            }
        )

        await self.repo.save(event)

        return followup_text