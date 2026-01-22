from fastapi import APIRouter, Depends
from backend.api.middleware import require_any_auth
from services.executive_documents_service import ExecutiveDocumentsService

router = APIRouter(prefix="/executive-docs", tags=["Executive Documents"])


@router.get("/daily")
async def daily_doc(current_user=Depends(require_any_auth)):
    service = ExecutiveDocumentsService(current_user["id"])
    return service.generate_daily()


@router.get("/weekly")
async def weekly_doc(current_user=Depends(require_any_auth)):
    service = ExecutiveDocumentsService(current_user["id"])
    return service.generate_weekly()


@router.get("/board")
async def board_doc(current_user=Depends(require_any_auth)):
    service = ExecutiveDocumentsService(current_user["id"])
    return service.generate_board()
