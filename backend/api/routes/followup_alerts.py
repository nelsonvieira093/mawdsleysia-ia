from fastapi import APIRouter, Depends
from backend.api.middleware import require_any_auth
from services.followup_alert_service import FollowUpAlertService

router = APIRouter(prefix="/followup-alerts", tags=["FollowUp Alerts"])


@router.get("/forgotten")
async def forgotten_followups(current_user=Depends(require_any_auth)):
    service = FollowUpAlertService(current_user["id"])
    return service.forgotten_followups()
