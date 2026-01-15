from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import date, timedelta

from models.followup import FollowUp


class KPIRepository:
    def __init__(self, db: Session):
        self.db = db

    # ============================================================
    # 📌 KPI — FOLLOW-UPS
    # ============================================================

    def followup_summary(self, user_id: int) -> dict:
        today = date.today()
        start_of_week = today - timedelta(days=today.weekday())

        open_count = (
            self.db.query(func.count(FollowUp.id))
            .filter(
                FollowUp.owner_id == user_id,
                FollowUp.status == "ABERTO",
            )
            .scalar()
        )

        overdue_count = (
            self.db.query(func.count(FollowUp.id))
            .filter(
                FollowUp.owner_id == user_id,
                FollowUp.status == "ABERTO",
                FollowUp.due_date.isnot(None),
                FollowUp.due_date < today,
            )
            .scalar()
        )

        created_this_week = (
            self.db.query(func.count(FollowUp.id))
            .filter(
                FollowUp.owner_id == user_id,
                FollowUp.created_at >= start_of_week,
            )
            .scalar()
        )

        # ✅ STATUS CORRETO DO ENUM (AJUSTADO)
        closed_this_week = (
            self.db.query(func.count(FollowUp.id))
            .filter(
                FollowUp.owner_id == user_id,
                FollowUp.status == "CONCLUIDO",  # 👈 AJUSTE AQUI
                FollowUp.created_at >= start_of_week,
            )
            .scalar()
        )

        return {
            "open": open_count,
            "overdue": overdue_count,
            "created_this_week": created_this_week,
            "closed_this_week": closed_this_week,
        }

    # ============================================================
    # ⏱️ KPI — PERFORMANCE
    # ============================================================

    def followup_performance(self, user_id: int) -> dict:
        total = (
            self.db.query(func.count(FollowUp.id))
            .filter(FollowUp.owner_id == user_id)
            .scalar()
        )

        closed = (
            self.db.query(func.count(FollowUp.id))
            .filter(
                FollowUp.owner_id == user_id,
                FollowUp.status == "CONCLUIDO",  # 👈 AJUSTE AQUI
            )
            .scalar()
        )

        closure_rate = (closed / total * 100) if total else 0

        return {
            "avg_close_days": 0.0,
            "closure_rate": round(closure_rate, 1),
        }

    # ============================================================
    # 📆 KPI — AGENDA
    # ============================================================

    def agenda_kpis(self, user_id: int) -> dict:
        today = date.today()
        next_7_days = today + timedelta(days=7)

        due_today = (
            self.db.query(func.count(FollowUp.id))
            .filter(
                FollowUp.owner_id == user_id,
                FollowUp.status == "ABERTO",
                FollowUp.due_date == today,
            )
            .scalar()
        )

        due_next_7_days = (
            self.db.query(func.count(FollowUp.id))
            .filter(
                FollowUp.owner_id == user_id,
                FollowUp.status == "ABERTO",
                FollowUp.due_date.isnot(None),
                FollowUp.due_date > today,
                FollowUp.due_date <= next_7_days,
            )
            .scalar()
        )

        return {
            "due_today": due_today,
            "due_next_7_days": due_next_7_days,
        }
# E:\MAWDSLEYS-AGENTE\backend\db\repositories\kpi_repository.py