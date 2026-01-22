from datetime import datetime, timedelta
from database.session import SessionLocal
from models.capture import Capture


class ExecutiveDocumentsService:
    """
    Geração automática de documentos executivos:
    Daily / Weekly / Board
    """

    def __init__(self, user_id: str):
        self.user_id = user_id
        self.db = SessionLocal()

    def _base_query(self, since):
        return (
            self.db.query(Capture)
            .filter(Capture.user_id == self.user_id)
            .filter(Capture.created_at >= since)
            .order_by(Capture.created_at.asc())
            .all()
        )

    def generate_daily(self):
        since = datetime.utcnow() - timedelta(days=1)
        captures = self._base_query(since)

        return {
            "type": "DailyLog",
            "date": datetime.utcnow().date().isoformat(),
            "items": captures
        }

    def generate_weekly(self):
        since = datetime.utcnow() - timedelta(days=7)
        captures = self._base_query(since)

        return {
            "type": "WeeklyDigest",
            "week": datetime.utcnow().isocalendar()[1],
            "items": captures
        }

    def generate_board(self):
        since = datetime.utcnow() - timedelta(days=30)
        captures = self._base_query(since)

        board_items = [
            c for c in captures
            if "#BoardReport" in (c.hashtags or [])
            or "#Decision" in (c.hashtags or [])
        ]

        return {
            "type": "BoardReport",
            "month": datetime.utcnow().month,
            "items": board_items
        }
