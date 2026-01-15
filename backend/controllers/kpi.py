# backend/controllers/kpi.py
from sqlalchemy.orm import Session

def get_kpis(db: Session):
    return []

def get_kpi(db: Session, kpi_id: int):
    return None

def get_user_kpis(db: Session, user_id: int):
    return []

def create_kpi(db: Session, payload: dict):
    return {"status": "created", "payload": payload}

def update_kpi(db: Session, kpi_id: int, payload: dict):
    return {"status": "updated", "kpi_id": kpi_id, "payload": payload}

def delete_kpi(db: Session, kpi_id: int):
    return {"status": "deleted", "kpi_id": kpi_id}
