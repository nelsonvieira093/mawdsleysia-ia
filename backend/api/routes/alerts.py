from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from db.session import get_db
from ...middleware.auth import require_any_auth
from db.models.activity_log import ActivityLog

router = APIRouter(prefix="/api/v1/alerts", tags=["Alerts"])

@router.get("")
def get_alerts(
    db: Session = Depends(get_db),
    user=Depends(require_any_auth)
):
    alerts = (
        db.query(ActivityLog)
        .filter(ActivityLog.type == "alert.created")
        .order_by(ActivityLog.timestamp.desc())
        .limit(20)
        .all()
    )

    return [
        {
            "id": a.entity_id,
            "level": a.payload.get("level"),
            "title": a.payload.get("title"),
            "description": a.payload.get("description"),
            "timestamp": a.timestamp.isoformat()
        }
        for a in alerts
    ]
