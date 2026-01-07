# db/repositories/kpi_repository.py

from sqlalchemy.orm import Session
from sqlalchemy import func, case
from datetime import datetime
from db.models.activity_log import ActivityLog


class KPIRepository:

    def __init__(self, db: Session):
        self.db = db

    def weekly_meetings_by_user(self):
        start_of_week = func.date_trunc('week', func.now())

        return (
            self.db.query(
                ActivityLog.user_id.label("user_id"),

                func.count().filter(
                    (ActivityLog.type == 'meeting') &
                    (ActivityLog.action == 'created')
                ).label("total_meetings"),

                func.count().filter(
                    (ActivityLog.type == 'meeting') &
                    (ActivityLog.action == 'started')
                ).label("meetings_started"),

                func.count().filter(
                    (ActivityLog.type == 'meeting') &
                    (ActivityLog.action == 'completed')
                ).label("meetings_completed"),

                func.count().filter(
                    (ActivityLog.type == 'meeting') &
                    (ActivityLog.action == 'cancelled')
                ).label("meetings_cancelled"),
            )
            .filter(
                ActivityLog.type == 'meeting',
                ActivityLog.created_at >= start_of_week
            )
            .group_by(ActivityLog.user_id)
            .order_by(func.count().filter(
                (ActivityLog.type == 'meeting') &
                (ActivityLog.action == 'created')
            ).desc())
            .all()
        )
