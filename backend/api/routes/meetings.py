# backend/api/routes/meetings.py - ATUALIZADO COM AUTH
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime

from backend.database.session import get_db
from backend.middleware.auth import require_any_auth
from backend.controllers.meeting import (
    get_meeting, get_meetings, get_user_meetings,
    create_meeting, update_meeting, delete_meeting
)
from backend.schemas.meeting import MeetingCreate, MeetingUpdate, MeetingResponse

router = APIRouter(prefix="/meetings", tags=["Meetings"])

# Rota pública para testes
@router.get("/public", response_model=List[MeetingResponse])
def get_meetings_public(
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db)
):
    """Listar todos os meetings (público para testes)"""
    items = get_meetings(db, skip=skip, limit=limit)
    return items

# Rotas protegidas
@router.get("/", response_model=List[MeetingResponse])
def get_user_meetings_route(
    skip: int = 0, 
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_any_auth)
):
    """Listar meetings do usuário atual"""
    user_id = current_user["user_id"]
    items = get_user_meetings(db, user_id=user_id, skip=skip, limit=limit)
    return items

@router.post("/", response_model=MeetingResponse, status_code=status.HTTP_201_CREATED)
def create_meeting_route(
    meeting: MeetingCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_any_auth)
):
    """Criar novo meeting"""
    user_id = current_user["user_id"]
    return create_meeting(db, meeting, user_id=user_id)

@router.get("/{meeting_id}", response_model=MeetingResponse)
def get_meeting_route(
    meeting_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_any_auth)
):
    """Buscar um meeting específico"""
    db_meeting = get_meeting(db, meeting_id)
    
    if not db_meeting:
        raise HTTPException(status_code=404, detail="Meeting não encontrado")
    
    if db_meeting.user_id != current_user["user_id"] and "admin" not in current_user["roles"]:
        raise HTTPException(status_code=403, detail="Acesso não autorizado")
    
    return db_meeting

@router.put("/{meeting_id}", response_model=MeetingResponse)
def update_meeting_route(
    meeting_id: int,
    meeting: MeetingUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_any_auth)
):
    """Atualizar meeting"""
    db_meeting = get_meeting(db, meeting_id)
    
    if not db_meeting:
        raise HTTPException(status_code=404, detail="Meeting não encontrado")
    
    if db_meeting.user_id != current_user["user_id"] and "admin" not in current_user["roles"]:
        raise HTTPException(status_code=403, detail="Acesso não autorizado")
    
    updated = update_meeting(db, meeting_id, meeting)
    return updated

@router.delete("/{meeting_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_meeting_route(
    meeting_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_any_auth)
):
    """Deletar meeting"""
    db_meeting = get_meeting(db, meeting_id)
    
    if not db_meeting:
        raise HTTPException(status_code=404, detail="Meeting não encontrado")
    
    if db_meeting.user_id != current_user["user_id"] and "admin" not in current_user["roles"]:
        raise HTTPException(status_code=403, detail="Acesso não autorizado")
    
    delete_meeting(db, meeting_id)
    return None
