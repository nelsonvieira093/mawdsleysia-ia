# backend/controllers/kpi_controller.py

from sqlalchemy.orm import Session

from db.repositories.kpi_repository import KPIRepository
from db.repositories.followup_repository import FollowUpRepository


class KPIController:
    """
    KPI Controller (VERSÃO PRODUTO)
    ===============================

    Responsável por:
    - Orquestrar KPIs reais
    - Separar visão EXECUTIVA x OPERACIONAL
    - Nunca calcular dados diretamente
    """

    @staticmethod
    def get_overview(*, db: Session, user_id: int) -> dict:
        # ==============================
        # OPERACIONAL
        # ==============================
        kpi_repo = KPIRepository(db)

        meetings = kpi_repo.weekly_meetings_by_user()

        open_followups = FollowUpRepository.list_by_user(
            db,
            user_id=user_id,
        )

        overdue_followups = FollowUpRepository.list_overdue(
            db,
            user_id=user_id,
        )

        # ==============================
        # EXECUTIVO (RESUMO)
        # ==============================
        executive_summary = {
            "total_followups": len(open_followups),
            "overdue_followups": len(overdue_followups),
            "meetings_this_week": sum(
                m.total_meetings for m in meetings
            ),
        }

        return {
            "executive": {
                "summary": executive_summary
            },
            "operational": {
                "meetings": [
                    {
                        "user_id": m.user_id,
                        "total_meetings": m.total_meetings,
                        "meetings_started": m.meetings_started,
                        "meetings_completed": m.meetings_completed,
                        "meetings_cancelled": m.meetings_cancelled,
                    }
                    for m in meetings
                ],
                "followups": {
                    "open": len(open_followups),
                    "overdue": len(overdue_followups),
                }
            }
        }
