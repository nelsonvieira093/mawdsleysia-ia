from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database.session import get_db
from services.ingest_service import process_ingest

router = APIRouter(tags=["Ingest"])

@router.post("/ingest")
def ingest(payload: dict, db: Session = Depends(get_db)):
    """
    Endpoint oficial de ingestão.
    Recebe texto bruto e persiste:
    - capture
    - note
    - followups
    """

    raw_text = payload.get("raw_text")

    if not raw_text:
        return {
            "status": "error",
            "message": "Campo 'raw_text' é obrigatório"
        }

    result = process_ingest(
        db=db,
        raw_text=raw_text,
        source="api"
    )

    return {
        "status": "ok",
        "result": result
    }
