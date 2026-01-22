from database.session import SessionLocal
from models.capture import Capture
from datetime import datetime, timedelta
from collections import Counter


class ExecutiveDashboardService:

    def __init__(self, user_id: str):
        self.user_id = user_id
        self.db = SessionLocal()

    def summary(self):
        since = datetime.utcnow() - timedelta(days=30)
        captures = (
            self.db.query(Capture)
            .filter(Capture.user_id == self.user_id)
            .filter(Capture.created_at >= since)
            .all()
        )

        hashtags = Counter(
            tag for c in captures for tag in (c.hashtags or [])
        )

        return {
            "total_captures": len(captures),
            "top_hashtags": hashtags.most_common(10),
            "last_30_days": len(captures)
        }
