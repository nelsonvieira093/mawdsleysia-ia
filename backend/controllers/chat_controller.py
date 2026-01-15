# backend/controllers/chat_controller.py

"""
Chat Controller
================

Responsável por:
- Orquestrar fluxo de chat
- Receber resposta da IA
- Criar Notes
- Disparar criação automática de FollowUps quando aplicável

⚠️ IMPORTANTE:
Este arquivo NÃO é rota.
Este arquivo NÃO fala direto com HTTP.
Aqui mora regra de negócio e orquestração.
"""

from typing import Optional

from sqlalchemy.orm import Session

from controllers.followup_controller import FollowUpController


# ============================================================
# 🔗 Integração Chat → FollowUp
# ============================================================

def maybe_create_followup_from_chat(
    *,
    db: Session,
    user_id: int,
    note_id,
    ai_text: str,
) -> Optional[dict]:
    """
    Analisa o texto gerado pela IA e decide
    se deve criar automaticamente um FollowUp.

    Estratégia atual:
    - Heurística simples por palavras-chave
    - Evoluível para NLP / classificação futura

    Retorna:
    - FollowUp criado (dict / model) ou None
    """

    if not ai_text:
        return None

    text = ai_text.lower()

    # 🔍 Triggers iniciais (heurística simples)
    triggers = [
        "vou",
        "preciso",
        "enviar",
        "ligar",
        "retornar",
        "follow-up",
        "ação",
        "verificar",
        "confirmar",
        "preparar",
        "agendar",
    ]

    if not any(trigger in text for trigger in triggers):
        return None

    # 🧠 Regra simples de prioridade
    priority = "MEDIA"
    if any(word in text for word in ["urgente", "hoje", "imediato"]):
        priority = "ALTA"

    # ✂️ Descrição segura
    description = ai_text.strip()[:500]

    # 🔥 Criação centralizada no FollowUpController
    followup = FollowUpController.create_followup(
        db=db,
        user_id=user_id,
        note_id=note_id,
        description=description,
        priority=priority,
        source="chat",
    )

    return followup
