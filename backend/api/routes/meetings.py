# backend/api/routes/meetings.py - VERSÃO ATUALIZADA
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field

from database.session import get_db
from api.routes.auth import require_any_auth

router = APIRouter(prefix="/meetings", tags=["Meetings"])

# ==========================
# SCHEMAS
# ==========================
class MeetingCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200, example="Reunião de Planejamento")
    description: Optional[str] = Field(None, max_length=1000, example="Discussão do planejamento trimestral")
    scheduled_time: datetime = Field(..., example="2024-01-15T10:00:00Z")
    duration_minutes: int = Field(60, ge=15, le=480, example=60)
    location: Optional[str] = Field(None, max_length=200, example="Sala de Reuniões 1")
    participants: Optional[List[int]] = Field(default_factory=list, example=[2, 3, 4])
    agenda: Optional[str] = Field(None, max_length=2000, example="1. Abertura\n2. Discussão de metas\n3. Próximos passos")

class MeetingUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    scheduled_time: Optional[datetime] = None
    duration_minutes: Optional[int] = Field(None, ge=15, le=480)
    location: Optional[str] = Field(None, max_length=200)
    status: Optional[str] = Field(None, pattern="^(scheduled|in_progress|completed|cancelled)$")
    agenda: Optional[str] = Field(None, max_length=2000)

class MeetingResponse(BaseModel):
    id: int
    title: str
    description: Optional[str]
    scheduled_time: datetime
    duration_minutes: int
    location: Optional[str]
    status: str
    organizer_id: int
    agenda: Optional[str]
    participants: List[int] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

# ==========================
# CONTROLLERS (definições locais temporárias)
# ==========================
class MeetingController:
    # Mock data para desenvolvimento
    _mock_meetings = [
        {
            "id": 1,
            "title": "Reunião de Planejamento",
            "description": "Planejamento trimestral",
            "scheduled_time": datetime.utcnow(),
            "duration_minutes": 60,
            "location": "Sala 1",
            "status": "scheduled",
            "organizer_id": 1,
            "agenda": "Discussão de metas",
            "participants": [2, 3],
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        },
        {
            "id": 2,
            "title": "Daily Standup",
            "description": "Reunião diária da equipe",
            "scheduled_time": datetime.utcnow(),
            "duration_minutes": 30,
            "location": "Virtual",
            "status": "scheduled",
            "organizer_id": 2,
            "agenda": "Updates diários",
            "participants": [1, 3, 4],
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
    ]
    
    @classmethod
    def get_meetings(cls, db: Session, user_id: int, skip: int = 0, limit: int = 100):
        """Mock - retorna reuniões do usuário"""
        user_meetings = [
            meeting for meeting in cls._mock_meetings 
            if meeting["organizer_id"] == user_id or user_id in meeting.get("participants", [])
        ]
        return user_meetings[skip:skip + limit]
    
    @classmethod
    def get_all_meetings(cls, db: Session, skip: int = 0, limit: int = 100):
        """Mock - retorna todas as reuniões (para rota pública)"""
        return cls._mock_meetings[skip:skip + limit]
    
    @classmethod
    def create_meeting(cls, db: Session, meeting_data: dict, user_id: int):
        """Mock - cria uma reunião de exemplo"""
        new_id = max(m["id"] for m in cls._mock_meetings) + 1 if cls._mock_meetings else 1
        
        new_meeting = {
            "id": new_id,
            "title": meeting_data.get("title", "Nova Reunião"),
            "description": meeting_data.get("description"),
            "scheduled_time": meeting_data.get("scheduled_time", datetime.utcnow()),
            "duration_minutes": meeting_data.get("duration_minutes", 60),
            "location": meeting_data.get("location"),
            "status": "scheduled",
            "organizer_id": user_id,
            "agenda": meeting_data.get("agenda"),
            "participants": meeting_data.get("participants", []),
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        cls._mock_meetings.append(new_meeting)
        return new_meeting
    
    @classmethod
    def get_meeting(cls, db: Session, meeting_id: int, user_id: Optional[int] = None):
        """Mock - retorna uma reunião específica"""
        for meeting in cls._mock_meetings:
            if meeting["id"] == meeting_id:
                # Verifica se o usuário tem acesso
                if user_id is not None:
                    if meeting["organizer_id"] != user_id and user_id not in meeting.get("participants", []):
                        return None
                return meeting
        return None
    
    @classmethod
    def update_meeting(cls, db: Session, meeting_id: int, meeting_data: dict, user_id: int):
        """Mock - atualiza uma reunião"""
        for i, meeting in enumerate(cls._mock_meetings):
            if meeting["id"] == meeting_id:
                # Verifica se o usuário é o organizador
                if meeting["organizer_id"] != user_id:
                    return None
                
                # Atualiza os campos
                update_data = {k: v for k, v in meeting_data.items() if v is not None}
                cls._mock_meetings[i].update(update_data)
                cls._mock_meetings[i]["updated_at"] = datetime.utcnow()
                
                return cls._mock_meetings[i]
        return None
    
    @classmethod
    def delete_meeting(cls, db: Session, meeting_id: int, user_id: int):
        """Mock - deleta uma reunião"""
        for i, meeting in enumerate(cls._mock_meetings):
            if meeting["id"] == meeting_id:
                # Verifica se o usuário é o organizador
                if meeting["organizer_id"] != user_id:
                    return False
                
                # Soft delete (muda status para cancelled)
                cls._mock_meetings[i]["status"] = "cancelled"
                cls._mock_meetings[i]["updated_at"] = datetime.utcnow()
                return True
        return False
    
    @classmethod
    def start_meeting(cls, db: Session, meeting_id: int, user_id: int):
        """Mock - inicia uma reunião"""
        for i, meeting in enumerate(cls._mock_meetings):
            if meeting["id"] == meeting_id:
                # Verifica se o usuário é o organizador
                if meeting["organizer_id"] != user_id:
                    return None
                
                cls._mock_meetings[i]["status"] = "in_progress"
                cls._mock_meetings[i]["started_at"] = datetime.utcnow()
                cls._mock_meetings[i]["updated_at"] = datetime.utcnow()
                return cls._mock_meetings[i]
        return None
    
    @classmethod
    def complete_meeting(cls, db: Session, meeting_id: int, user_id: int):
        """Mock - marca reunião como concluída"""
        for i, meeting in enumerate(cls._mock_meetings):
            if meeting["id"] == meeting_id:
                # Verifica se o usuário é o organizador
                if meeting["organizer_id"] != user_id:
                    return None
                
                cls._mock_meetings[i]["status"] = "completed"
                cls._mock_meetings[i]["completed_at"] = datetime.utcnow()
                cls._mock_meetings[i]["updated_at"] = datetime.utcnow()
                return cls._mock_meetings[i]
        return None

# ==========================
# ROTAS
# ==========================
@router.get("/public", response_model=List[MeetingResponse])
def get_meetings_public(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Listar todas as reuniões (público para testes)"""
    meetings = MeetingController.get_all_meetings(db, skip=skip, limit=limit)
    return meetings

@router.get("/", response_model=List[MeetingResponse])
def get_user_meetings(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_any_auth)
):
    """Listar reuniões do usuário"""
    user_id = current_user.get("user_id")
    if not user_id:
        raise HTTPException(status_code=401, detail="Usuário não autenticado")
    
    meetings = MeetingController.get_meetings(db, user_id, skip, limit)
    return meetings

@router.post("/", response_model=MeetingResponse, status_code=status.HTTP_201_CREATED)
def create_new_meeting(
    meeting: MeetingCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_any_auth)
):
    """Criar nova reunião"""
    user_id = current_user.get("user_id")
    if not user_id:
        raise HTTPException(status_code=401, detail="Usuário não autenticado")
    
    meeting_data = meeting.model_dump()
    new_meeting = MeetingController.create_meeting(db, meeting_data, user_id)
    return new_meeting

@router.get("/{meeting_id}", response_model=MeetingResponse)
def get_single_meeting(
    meeting_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_any_auth)
):
    """Buscar reunião específica"""
    user_id = current_user.get("user_id")
    if not user_id:
        raise HTTPException(status_code=401, detail="Usuário não autenticado")
    
    meeting = MeetingController.get_meeting(db, meeting_id, user_id)
    if not meeting:
        raise HTTPException(status_code=404, detail="Reunião não encontrada ou acesso não autorizado")
    
    return meeting

@router.put("/{meeting_id}", response_model=MeetingResponse)
def update_existing_meeting(
    meeting_id: int,
    meeting: MeetingUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_any_auth)
):
    """Atualizar reunião"""
    user_id = current_user.get("user_id")
    if not user_id:
        raise HTTPException(status_code=401, detail="Usuário não autenticado")
    
    update_data = meeting.model_dump(exclude_unset=True)
    updated = MeetingController.update_meeting(db, meeting_id, update_data, user_id)
    
    if not updated:
        raise HTTPException(
            status_code=404, 
            detail="Reunião não encontrada ou você não tem permissão para atualizá-la"
        )
    
    return updated

@router.delete("/{meeting_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_existing_meeting(
    meeting_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_any_auth)
):
    """Deletar reunião (soft delete)"""
    user_id = current_user.get("user_id")
    if not user_id:
        raise HTTPException(status_code=401, detail="Usuário não autenticado")
    
    success = MeetingController.delete_meeting(db, meeting_id, user_id)
    if not success:
        raise HTTPException(
            status_code=404,
            detail="Reunião não encontrada ou você não tem permissão para deletá-la"
        )
    
    return None

@router.post("/{meeting_id}/start", response_model=MeetingResponse)
def start_meeting_route(
    meeting_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_any_auth)
):
    """Iniciar uma reunião"""
    user_id = current_user.get("user_id")
    if not user_id:
        raise HTTPException(status_code=401, detail="Usuário não autenticado")
    
    started = MeetingController.start_meeting(db, meeting_id, user_id)
    if not started:
        raise HTTPException(
            status_code=404,
            detail="Reunião não encontrada ou você não tem permissão para iniciá-la"
        )
    
    return started

@router.post("/{meeting_id}/complete", response_model=MeetingResponse)
def complete_meeting_route(
    meeting_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_any_auth)
):
    """Marcar reunião como concluída"""
    user_id = current_user.get("user_id")
    if not user_id:
        raise HTTPException(status_code=401, detail="Usuário não autenticado")
    
    completed = MeetingController.complete_meeting(db, meeting_id, user_id)
    if not completed:
        raise HTTPException(
            status_code=404,
            detail="Reunião não encontrada ou você não tem permissão para concluí-la"
        )
    
    return completed

@router.get("/{meeting_id}/participants")
def get_meeting_participants(
    meeting_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_any_auth)
):
    """Listar participantes da reunião"""
    user_id = current_user.get("user_id")
    if not user_id:
        raise HTTPException(status_code=401, detail="Usuário não autenticado")
    
    meeting = MeetingController.get_meeting(db, meeting_id, user_id)
    if not meeting:
        raise HTTPException(
            status_code=404,
            detail="Reunião não encontrada ou acesso não autorizado"
        )
    
    return {
        "meeting_id": meeting_id,
        "title": meeting["title"],
        "participants": meeting.get("participants", []),
        "total_participants": len(meeting.get("participants", []))
    }

@router.get("/stats/summary")
def get_meetings_summary(
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_any_auth)
):
    """Obter estatísticas de reuniões do usuário"""
    user_id = current_user.get("user_id")
    if not user_id:
        raise HTTPException(status_code=401, detail="Usuário não autenticado")
    
    user_meetings = MeetingController.get_meetings(db, user_id, skip=0, limit=1000)
    
    scheduled = sum(1 for m in user_meetings if m["status"] == "scheduled")
    in_progress = sum(1 for m in user_meetings if m["status"] == "in_progress")
    completed = sum(1 for m in user_meetings if m["status"] == "completed")
    cancelled = sum(1 for m in user_meetings if m["status"] == "cancelled")
    
    # Próxima reunião agendada
    upcoming_meetings = [m for m in user_meetings if m["status"] == "scheduled"]
    next_meeting = min(upcoming_meetings, key=lambda x: x["scheduled_time"]) if upcoming_meetings else None
    
    return {
        "total_meetings": len(user_meetings),
        "scheduled": scheduled,
        "in_progress": in_progress,
        "completed": completed,
        "cancelled": cancelled,
        "next_meeting": {
            "id": next_meeting["id"] if next_meeting else None,
            "title": next_meeting["title"] if next_meeting else None,
            "scheduled_time": next_meeting["scheduled_time"] if next_meeting else None
        } if next_meeting else None
    }

@router.get("/health")
def meetings_health():
    """Health check para o módulo de meetings"""
    return {
        "status": "healthy",
        "service": "meetings",
        "timestamp": datetime.utcnow().isoformat(),
        "mock_data_count": len(MeetingController._mock_meetings)
    }