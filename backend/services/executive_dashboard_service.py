# E:\MAWDSLEYS-AGENTE\backend\services\executive_dashboard_service.py

from database.session import SessionLocal
from models.capture import Capture
from datetime import datetime, timedelta
from collections import Counter
from typing import List


class ExecutiveDashboardService:
    def __init__(self, user_id: str):
        self.user_id = user_id
        self.db = SessionLocal()

    # =====================================================
    # RESUMO GERAL (mantido – usado por /summary se existir)
    # =====================================================
    def summary(self):
        since = datetime.utcnow() - timedelta(days=30)

        captures = (
            self.db.query(Capture)
            .filter(Capture.user_id == self.user_id)
            .filter(Capture.created_at >= since)
            .order_by(Capture.created_at.desc())
            .all()
        )

        hashtags = Counter(
            tag for c in captures for tag in (c.hashtags or [])
        )

        return {
            "total_captures": len(captures),
            "top_hashtags": hashtags.most_common(10),
            "last_30_days": len(captures),
        }

    # =====================================================
    # VISÕES EXECUTIVAS (Daily / Weekly / Board)
    # =====================================================
    def get_view(self, view: str) -> List[dict]:
        """
        Retorna itens estruturados para o Dashboard Executivo
        view: daily | weekly | board
        """

        now = datetime.utcnow()

        if view == "daily":
            since = now - timedelta(days=1)
        elif view == "weekly":
            since = now - timedelta(days=7)
        elif view == "board":
            since = now - timedelta(days=30)
        else:
            since = now - timedelta(days=1)

        captures = (
            self.db.query(Capture)
            .filter(Capture.user_id == self.user_id)
            .filter(Capture.created_at >= since)
            .order_by(Capture.created_at.desc())
            .all()
        )

        items = []

        for c in captures:
            items.append({
                "id": str(c.id),
                "summary": c.summary or c.content[:180],
                "hashtags": c.hashtags or [],
                "followups": c.followups or [],
                "rituals": c.rituals or [],
                "directors": c.directors or [],
                "actions": c.actions or [],
                "register_location": c.source or "chat",
                "created_at": c.created_at.isoformat(),
            })

        return items
