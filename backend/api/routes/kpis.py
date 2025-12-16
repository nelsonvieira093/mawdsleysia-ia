# backend/api/routes/kpis.py - ATUALIZADO COM AUTH
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from backend.database.session import get_db
from backend.middleware.auth import require_any_auth
from backend.controllers.kpi import (
    get_kpi, get_kpis, get_user_kpis,
    create_kpi, update_kpi, delete_kpi
)
from backend.schemas.kpi import KPICreate, KPIUpdate, KPIResponse

router = APIRouter(prefix="/kpis", tags=["KPIs"])

# Rota pública para testes
@router.get("/public", response_model=List[KPIResponse])
def get_kpis_public(
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db)
):
    """Listar todos os KPIs (público para testes)"""
    items = get_kpis(db, skip=skip, limit=limit)
    return items

# Rotas protegidas
@router.get("/", response_model=List[KPIResponse])
def get_user_kpis_route(
    skip: int = 0, 
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_any_auth)
):
    """Listar KPIs do usuário atual"""
    user_id = current_user["user_id"]
    items = get_user_kpis(db, user_id=user_id, skip=skip, limit=limit)
    return items

@router.post("/", response_model=KPIResponse, status_code=status.HTTP_201_CREATED)
def create_kpi_route(
    kpi: KPICreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_any_auth)
):
    """Criar novo KPI"""
    user_id = current_user["user_id"]
    return create_kpi(db, kpi, user_id=user_id)

@router.get("/{kpi_id}", response_model=KPIResponse)
def get_kpi_route(
    kpi_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_any_auth)
):
    """Buscar um KPI específico"""
    db_kpi = get_kpi(db, kpi_id)
    
    if not db_kpi:
        raise HTTPException(status_code=404, detail="KPI não encontrado")
    
    if db_kpi.user_id != current_user["user_id"] and "admin" not in current_user["roles"]:
        raise HTTPException(status_code=403, detail="Acesso não autorizado")
    
    return db_kpi

@router.put("/{kpi_id}", response_model=KPIResponse)
def update_kpi_route(
    kpi_id: int,
    kpi: KPIUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_any_auth)
):
    """Atualizar KPI"""
    db_kpi = get_kpi(db, kpi_id)
    
    if not db_kpi:
        raise HTTPException(status_code=404, detail="KPI não encontrado")
    
    if db_kpi.user_id != current_user["user_id"] and "admin" not in current_user["roles"]:
        raise HTTPException(status_code=403, detail="Acesso não autorizado")
    
    updated = update_kpi(db, kpi_id, kpi)
    return updated

@router.delete("/{kpi_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_kpi_route(
    kpi_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_any_auth)
):
    """Deletar KPI"""
    db_kpi = get_kpi(db, kpi_id)
    
    if not db_kpi:
        raise HTTPException(status_code=404, detail="KPI não encontrado")
    
    if db_kpi.user_id != current_user["user_id"] and "admin" not in current_user["roles"]:
        raise HTTPException(status_code=403, detail="Acesso não autorizado")
    
    delete_kpi(db, kpi_id)
    return None
