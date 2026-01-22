from datetime import datetime, timedelta
from typing import List
from sqlalchemy.orm import Session

from database.session import SessionLocal
from models.capture import Capture


class ExecutiveMemoryService:
    """
    Memória executiva persistente da CEO.
    Fonte da verdade: tabela captures.
    """

    def __init__(self, user_id: str):
        self.user_id = user_id
        self.db: Session = SessionLocal()

    def get_recent_captures(
        self,
        days: int = 30,
        limit: int = 20
    ) -> List[Capture]:
        since = datetime.utcnow() - timedelta(days=days)

        return (
            self.db.query(Capture)
            .filter(Capture.user_id == self.user_id)
            .filter(Capture.created_at >= since)
            .order_by(Capture.created_at.desc())
            .limit(limit)
            .all()
        )

    def build_context(self, days: int = 30, limit: int = 20) -> str:
        captures = self.get_recent_captures(days=days, limit=limit)

        blocks = []

        for c in captures:
            blocks.append(
                f"""
DATA: {c.created_at}
HASHTAGS: {', '.join(c.hashtags or [])}
RITOS: {', '.join(c.rituals or [])}
RESUMO: {c.structured_summary.get('summary')}
AÇÕES: {c.structured_summary.get('actions')}
"""
            )

        return "\n---\n".join(blocks)
