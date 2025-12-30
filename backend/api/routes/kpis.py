from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

from database.session import get_db
from models.followup import FollowUp
from models.ritual import Ritual

router = APIRouter(prefix="/kpis", tags=["KPIs"])


@router.get("/followups/summary")
def followups_summary(db: Session = Depends(get_db)):
    """
    KPI geral:
    - total de followups
    - quantos abertos
    - quantos em andamento
    - quantos concluídos
    """

    total = db.query(FollowUp).count()

    abertos = db.query(FollowUp).filter(FollowUp.status == "ABERTO").count()
    em_andamento = db.query(FollowUp).filter(FollowUp.status == "EM_ANDAMENTO").count()
    concluidos = db.query(FollowUp).filter(FollowUp.status == "CONCLUIDO").count()

    return {
        "total_followups": total,
        "abertos": abertos,
        "em_andamento": em_andamento,
        "concluidos": concluidos,
    }


@router.get("/followups/by-ritual")
def followups_by_ritual(db: Session = Depends(get_db)):
    """
    KPI por ritual:
    Quantidade de followups agrupados por ritual
    """

    rows = (
        db.query(
            Ritual.code.label("ritual"),
            func.count(FollowUp.id).label("total")
        )
        .outerjoin(FollowUp, FollowUp.ritual_id == Ritual.id)
        .group_by(Ritual.code)
        .all()
    )

    return [
        {
            "ritual": r.ritual,
            "total_followups": r.total
        }
        for r in rows
    ]
