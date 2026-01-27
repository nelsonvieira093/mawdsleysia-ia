# E:\MAWDSLEYS-AGENTE\backend\api\routes\executive_dashboard.py

from fastapi import APIRouter, Depends
from api.middleware import require_any_auth
from services.executive_dashboard_service import ExecutiveDashboardService

router = APIRouter(prefix="/executive-dashboard", tags=["Executive Dashboard"])


@router.get("/summary")
async def dashboard_summary(current_user=Depends(require_any_auth)):
    service = ExecutiveDashboardService(current_user["id"])
    return service.summary()
