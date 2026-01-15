from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy.sql import func

from database.session import get_db
from api.routes.auth import require_any_auth

from controllers.automation_controller import AutomationController
from db.repositories.kpi_repository import KPIRepository
from db.repositories.activity_log_repository import ActivityLogRepository
from core.events.activity_log import ActivityEvent
from db.models.activity_log import ActivityLog


# Router declarado antes de uso
router = APIRouter(
    prefix="/api/v1/automations",
    tags=["Automations"],
)


@router.post("/run-followups")
def run_followup_automation(
    db: Session = Depends(get_db),
    user=Depends(require_any_auth),
):
    """
    Automação diária de FollowUps:
    - Reclassifica vencidos
    - Prepara agenda
    - Base para notificações
    """
    return AutomationController.run_daily_followup_automation(
        db=db,
        user_id=user.id,
    )


@router.post("/check-weekly-meetings")
def check_weekly_meetings(
    db: Session = Depends(get_db),
):
    """
    Automação mínima:
    Gera alerta para usuários sem reuniões na semana atual
    SEM duplicar alertas
    """

    # ID fixo utilizado no contexto atual
    user_id = 1

    kpi_repo = KPIRepository(db)
    activity_repo = ActivityLogRepository(db)

    results = kpi_repo.weekly_meetings_by_user()

    alerts_created = []

    for row in results:

        already_exists = (
            db.query(ActivityLog)
            .filter(
                ActivityLog.type == "alert",
                ActivityLog.action == "created",
                ActivityLog.entity == f"user:{row.user_id}",
                ActivityLog.details == "Usuário sem reuniões registradas na semana atual",
                ActivityLog.created_at >= func.date_trunc("week", func.now()),
            )
            .first()
        )

        if already_exists:
            continue

        if row.total_meetings == 0:
            event = ActivityEvent(
                type="alert",
                action="created",
                entity=f"user:{row.user_id}",
                user_id=user_id,
                details="Usuário sem reuniões registradas na semana atual",
            )

            activity_repo.log(event)
            alerts_created.append(row.user_id)

    return {
        "status": "ok",
        "alerts_created_for_users": alerts_created,
        "total_alerts": len(alerts_created),
    }
