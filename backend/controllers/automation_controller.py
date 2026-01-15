# backend/controllers/automation_controller.py

"""
Automation Controller (VERSÃO PRODUTO)
=====================================

Responsável por:
- Executar automações do sistema
- Criar / fechar / atualizar FollowUps
- Ser executado manualmente ou via scheduler
"""

from datetime import date, timedelta
from sqlalchemy.orm import Session

from db.repositories.followup_repository import FollowUpRepository
from controllers.followup_controller import FollowUpController


class AutomationController:

    # --------------------------------------------------------
    # 🔁 ROTINA PRINCIPAL
    # --------------------------------------------------------
    @staticmethod
    def run_daily_followup_automation(
        *,
        db: Session,
        user_id: int,
    ) -> dict:
        """
        Executa automações diárias relacionadas a FollowUps.
        """

        today = date.today()

        # ---------------------------------------------
        # 1️⃣ Follow-ups vencidos
        # ---------------------------------------------
        overdue = FollowUpRepository.list_overdue(
            db,
            user_id=user_id,
        )

        escalated = 0

        for followup in overdue:
            if followup.priority != "ALTA":
                FollowUpController.update_followup(
                    db=db,
                    followup_id=followup.id,
                    user_id=user_id,
                    priority="ALTA",
                )
                escalated += 1

        # ---------------------------------------------
        # 2️⃣ Follow-ups para hoje (lembrete)
        # ---------------------------------------------
        today_followups = FollowUpRepository.list_due_soon(
            db,
            user_id=user_id,
            days_ahead=0,
        )

        # ---------------------------------------------
        # Resultado
        # ---------------------------------------------
        return {
            "date": today.isoformat(),
            "summary": {
                "overdue_found": len(overdue),
                "priority_escalated": escalated,
                "due_today": len(today_followups),
            },
        }
