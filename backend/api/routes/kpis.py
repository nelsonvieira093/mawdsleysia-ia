# backend/api/routes/kpis.py

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

from database.session import get_db
from api.routes.auth import require_any_auth


from db.repositories.kpi_repository import KPIRepository
from controllers.kpi_controller import KPIController

from models.followup import FollowUp
from models.ritual import Ritual
from db.models.activity_log import ActivityLog


router = APIRouter(
    prefix="/kpis",
    tags=["KPIs"]
)

# =========================================================
# 🔹 FOLLOWUPS — KPI GERAL (MANTIDO)
# =========================================================

@router.get("/followups/summary")
def followups_summary(
    db: Session = Depends(get_db),
    user=Depends(require_any_auth),
):
    """
    KPI geral de FollowUps (REAL):
    - total
    - abertos
    - em andamento
    - concluídos
    """

    total = (
        db.query(FollowUp)
        .filter(FollowUp.user_id == user.id)
        .count()
    )

    abertos = (
        db.query(FollowUp)
        .filter(
            FollowUp.user_id == user.id,
            FollowUp.status == "ABERTO"
        )
        .count()
    )

    em_andamento = (
        db.query(FollowUp)
        .filter(
            FollowUp.user_id == user.id,
            FollowUp.status == "EM_ANDAMENTO"
        )
        .count()
    )

    concluidos = (
        db.query(FollowUp)
        .filter(
            FollowUp.user_id == user.id,
            FollowUp.status == "CONCLUIDO"
        )
        .count()
    )

    return {
        "total_followups": total,
        "abertos": abertos,
        "em_andamento": em_andamento,
        "concluidos": concluidos,
    }


# =========================================================
# 🔹 FOLLOWUPS — KPI POR RITUAL (MANTIDO)
# =========================================================

@router.get("/followups/by-ritual")
def followups_by_ritual(
    db: Session = Depends(get_db),
    user=Depends(require_any_auth),
):
    """
    KPI de FollowUps agrupados por Ritual
    """

    rows = (
        db.query(
            Ritual.code.label("ritual"),
            func.count(FollowUp.id).label("total")
        )
        .outerjoin(
            FollowUp,
            (FollowUp.ritual_id == Ritual.id) &
            (FollowUp.user_id == user.id)
        )
        .group_by(Ritual.code)
        .order_by(func.count(FollowUp.id).desc())
        .all()
    )

    return [
        {
            "ritual": r.ritual,
            "total_followups": r.total
        }
        for r in rows
    ]


# =========================================================
# 🔹 MEETINGS — KPI OPERACIONAL (SEMANA) (MANTIDO)
# =========================================================

@router.get("/meetings/weekly")
def weekly_meetings_kpi(
    db: Session = Depends(get_db),
    user=Depends(require_any_auth),
):
    """
    KPI operacional:
    Reuniões por usuário na semana atual
    (baseado em ActivityLog)
    """

    repo = KPIRepository(db)
    return repo.weekly_meetings_by_user()


# =========================================================
# 🔹 KPI OVERVIEW — EXECUTIVO + OPERACIONAL (NOVO)
# =========================================================

@router.get("/overview")
def get_kpi_overview(
    db: Session = Depends(get_db),
    user=Depends(require_any_auth),
):
    """
    KPI EXECUTIVO CONSOLIDADO (PRODUTO):
    - Summary executivo
    - KPIs operacionais reais
    """

    return KPIController.get_overview(
        db=db,
        user_id=user.id,
    )
