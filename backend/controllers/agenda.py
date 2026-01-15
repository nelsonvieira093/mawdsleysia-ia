# backend/controllers/agenda.py

"""
Agenda Controller (VERSÃO PRODUTO)
=================================

Constrói agendas inteligentes baseadas em FollowUps reais,
mantendo o conceito de rituais.

❌ Sem FastAPI
❌ Sem HTTP
❌ Sem mocks
"""

from datetime import date
from sqlalchemy.orm import Session

from db.repositories.followup_repository import FollowUpRepository


# ============================================================
# 🗂️ TEMPLATES DE RITUAIS
# ============================================================

RITUAL_TEMPLATES = {
    "ONE_ON_ONE_ELSA": {
        "title": "Pauta One-on-One – Elsa",
        "sections": [
            "Follow-ups em aberto",
            "Follow-ups atrasados",
            "Próximos 7 dias",
        ],
    },
    "STAFF_MEETING": {
        "title": "Pauta Staff Meeting",
        "sections": [
            "Follow-ups críticos",
            "Pendências transversais",
            "Decisões executivas",
        ],
    },
}


# ============================================================
# 🧠 BUILDER PRINCIPAL
# ============================================================

def build_agenda(
    *,
    db: Session,
    user_id: int,
    ritual_code: str,
) -> dict:
    """
    Constrói agenda REAL a partir de FollowUps do banco.
    """

    template = RITUAL_TEMPLATES.get(ritual_code)

    if not template:
        return {
            "ritual": ritual_code,
            "error": "Rito não encontrado",
        }

    overdue = FollowUpRepository.list_overdue(
        db,
        user_id=user_id,
    )

    upcoming = FollowUpRepository.list_due_soon(
        db,
        user_id=user_id,
        days_ahead=7,
    )

    open_followups = FollowUpRepository.list_by_user(
        db,
        user_id=user_id,
    )

    agenda_sections = {}

    if "Follow-ups em aberto" in template["sections"]:
        agenda_sections["Follow-ups em aberto"] = open_followups

    if "Follow-ups atrasados" in template["sections"]:
        agenda_sections["Follow-ups atrasados"] = overdue

    if "Próximos 7 dias" in template["sections"]:
        agenda_sections["Próximos 7 dias"] = upcoming

    return {
        "ritual": ritual_code,
        "agenda": {
            "title": template["title"],
            "generated_at": date.today().isoformat(),
            "summary": {
                "open": len(open_followups),
                "overdue": len(overdue),
                "upcoming": len(upcoming),
            },
            "sections": agenda_sections,
        },
    }
