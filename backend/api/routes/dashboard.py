from datetime import datetime
import json

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database.session import get_db
from api.routes.auth import require_any_auth
from db.repositories.activity_log_repository import ActivityLogRepository

router = APIRouter(prefix="/api/dashboard", tags=["Dashboard"])


@router.get("/overview")
async def dashboard_overview(
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_any_auth)
):
    """
    Dashboard executivo — visão geral do sistema MAWDSLEYS
    Nunca deve falhar.
    """
    if not current_user:
        raise HTTPException(status_code=401, detail="Usuário não autenticado")

    repo = ActivityLogRepository(db)

    try:
        critical_alerts = await repo.list_critical_alerts(days=1)
    except Exception as e:
        print(f"[Dashboard] Erro ao buscar alertas: {e}")
        critical_alerts = []

    items = []
    for alert in critical_alerts:
        try:
            details = json.loads(alert.details) if alert.details else {}
        except Exception:
            details = {"raw": alert.details}

        items.append(
            {
                "id": alert.id,
                "created_at": alert.created_at.isoformat() if alert.created_at else None,
                "title": details.get("title", "Alerta crítico"),
                "description": details.get("description"),
                "source_event_id": details.get("source_event_id"),
            }
        )

    return {
        "timestamp": datetime.utcnow().isoformat(),
        "user": {
            "id": current_user.get("user_id"),
            "name": current_user.get("name"),
            "role": current_user.get("role"),
            "is_admin": current_user.get("is_admin", False),
        },
        "alerts": {
            "critical_today": len(items),
            "items": items,
        },
        "system": {
            "status": "operational",
            "audit_enabled": True,
            "automation_enabled": True,
            "email_enabled": True,
            "whatsapp_enabled": False,  # passo 3
        },
    }
