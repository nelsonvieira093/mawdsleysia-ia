# backend/api/routes/agenda.py

"""
Agenda Routes — VERSÃO PRODUTO
==============================

Expõe:
- Agenda por ritual (ONE_ON_ONE, STAFF, etc.)
- Agenda semanal executiva (follow-ups reais)

❌ Sem duplicação de router
❌ Sem lógica de negócio
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database.session import get_db
from api.routes.auth import require_any_auth


from controllers.agenda import build_agenda


router = APIRouter(prefix="/agenda", tags=["Agenda"])


# =========================================================
# 📌 AGENDA POR RITUAL (ex: ONE_ON_ONE_ELSA)
# =========================================================
@router.get("/ritual/{ritual_code}")
def get_agenda_by_ritual(
    ritual_code: str,
    db: Session = Depends(get_db),
    user=Depends(require_any_auth),
):
    """
    Retorna agenda estruturada por ritual.
    """
    return build_agenda(
        db=db,
        user_id=user.id,
        ritual_code=ritual_code,
    )


# =========================================================
# 📌 AGENDA SEMANAL EXECUTIVA (REAL)
# =========================================================
@router.get("/weekly")
def get_weekly_agenda(
    db: Session = Depends(get_db),
    user=Depends(require_any_auth),
):
    """
    Retorna agenda executiva semanal baseada em FollowUps reais.
    """
    return AgendaController.weekly_agenda(
        db=db,
        user_id=user.id,
    )
