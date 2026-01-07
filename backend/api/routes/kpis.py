from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

from database.session import get_db
from api.routes.auth import require_any_auth

from models.followup import FollowUp
from models.ritual import Ritual
from db.models.activity_log import ActivityLog
from db.repositories.kpi_repository import KPIRepository


router = APIRouter(
    prefix="/api/v1/kpis",
    tags=["KPIs"]
)

# =========================================================
# FOLLOWUPS — KPIs EXISTENTES (MANTIDOS)
# =========================================================

@router.get(
    "/followups/summary",
    dependencies=[Depends(require_any_auth)]
)

def followups_summary(db: Session = Depends(get_db)):
    """
    KPI geral de FollowUps:
    - total
    - abertos
    - em andamento
    - concluídos
    """

    total = db.query(FollowUp).count()

    abertos = (
        db.query(FollowUp)
        .filter(FollowUp.status == "ABERTO")
        .count()
    )

    em_andamento = (
        db.query(FollowUp)
        .filter(FollowUp.status == "EM_ANDAMENTO")
        .count()
    )

    concluidos = (
        db.query(FollowUp)
        .filter(FollowUp.status == "CONCLUIDO")
        .count()
    )

    return {
        "total_followups": total,
        "abertos": abertos,
        "em_andamento": em_andamento,
        "concluidos": concluidos,
    }


@router.get(
    "/followups/by-ritual",
    dependencies=[Depends(require_any_auth)]
)

def followups_by_ritual(db: Session = Depends(get_db)):
    """
    KPI de FollowUps agrupados por Ritual
    """

    rows = (
        db.query(
            Ritual.code.label("ritual"),
            func.count(FollowUp.id).label("total")
        )
        .outerjoin(FollowUp, FollowUp.ritual_id == Ritual.id)
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
# MEETINGS — KPI EXECUTIVO NOVO (SEMANA)
# =========================================================

@router.get(
    "/meetings/weekly",
    dependencies=[Depends(require_any_auth)]
)

def weekly_meetings_kpi(db: Session = Depends(get_db)):
    """
    KPI executivo:
    Reuniões por usuário na semana atual
    (baseado em ActivityLog auditável)
    """

    repo = KPIRepository(db)
    return repo.weekly_meetings_by_user()
