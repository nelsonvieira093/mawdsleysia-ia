from datetime import datetime, timedelta
from database.session import SessionLocal
from models.capture import Capture


class FollowUpAlertService:

    def __init__(self, user_id: str):
        self.user_id = user_id
        self.db = SessionLocal()

    def forgotten_followups(self, days: int = 7):
        since = datetime.utcnow() - timedelta(days=days)

        captures = (
            self.db.query(Capture)
            .filter(Capture.user_id == self.user_id)
            .filter(Capture.created_at <= since)
            .all()
        )

        alerts = []

        for c in captures:
            if c.followups and len(c.followups) > 0:
                alerts.append({
                    "capture_id": str(c.id),
                    "created_at": c.created_at,
                    "followups": c.followups
                })

        return alerts
