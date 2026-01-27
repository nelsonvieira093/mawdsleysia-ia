# E:\MAWDSLEYS-AGENTE\backend\api\routes\followup_alerts.py

from fastapi import APIRouter, Depends
from api.middleware import require_any_auth
from services.followup_alert_service import FollowUpAlertService

router = APIRouter(
    prefix="/followup-alerts",
    tags=["FollowUp Alerts"]
)

# =====================================================
# ENDPOINT PRINCIPAL (USADO PELO DASHBOARD)
# GET /api/followup-alerts
# =====================================================
@router.get("")
@router.get("/")
async def list_followup_alerts(current_user=Depends(require_any_auth)):
    """
    Retorna follow-ups em atraso para alerta visual no dashboard.
    Formato simples: lista de itens.
    """
    service = FollowUpAlertService(current_user["id"])

    alerts = service.forgotten_followups()

    # 🔒 Garantia de formato estável para frontend
    if not alerts:
        return []

    return alerts


# =====================================================
# ENDPOINT ESPECÍFICO (USO FUTURO / DEBUG)
# GET /api/followup-alerts/forgotten
# =====================================================
@router.get("/forgotten")
async def forgotten_followups(current_user=Depends(require_any_auth)):
    """
    Retorna follow-ups esquecidos (endpoint explícito).
    """
    service = FollowUpAlertService(current_user["id"])
    return service.forgotten_followups()
