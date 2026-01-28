from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database.session import get_db
from api.routes.auth import require_any_auth
from models.executive_journal import ExecutiveJournal

router = APIRouter(
    prefix="/api/v1/executive-journals",
    tags=["Executive Journal"],
)

@router.get("")
def list_executive_journals(
    current_user: dict = Depends(require_any_auth),
    db: Session = Depends(get_db),
):
    user_id = current_user.get("user_id")

    journals = (
        db.query(ExecutiveJournal)
        .filter(ExecutiveJournal.user_id == user_id)
        .order_by(ExecutiveJournal.created_at.desc())
        .all()
    )

    return [
        {
            "id": j.id,
            "summary": j.summary,
            "alerts": j.alerts,
            "followups": j.followups,
            "actions": j.actions,
            "decisions": j.decisions,
            "tags": j.tags,
            "created_at": j.created_at.isoformat(),
        }
        for j in journals
    ]
