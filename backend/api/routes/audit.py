#  E:\MAWDSLEYS-AGENTE\backend\api\routes\audit.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database.session import get_db
from db.models.activity_log import ActivityLog

router = APIRouter(prefix="/audit", tags=["Auditoria"])


@router.get("/alerts")
def audit_alerts(db: Session = Depends(get_db)):
    """
    Retorna histórico completo de alertas gerados
    (compliance / auditoria)
    """
    logs = (
        db.query(ActivityLog)
        .filter(ActivityLog.action == "alert.created")
        .order_by(ActivityLog.created_at.desc())
        .all()
    )

    return logs
