# E:\MAWDSLEYS-AGENTE\backend\api\routes\meetings.py - VERSÃO ATUALIZADA
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field
from fastapi import APIRouter

# 🔹 IMPORTS DO SISTEMA
from database.session import get_db
from api.routes.auth import require_any_auth

# 🔹 CONTROLLERS
from controllers.meeting import (
    get_meeting as db_get_meeting,
    get_meetings as db_get_meetings,
    create_meeting as db_create_meeting,
    update_meeting as db_update_meeting,
    delete_meeting as db_delete_meeting,
    start_meeting as db_start_meeting,
    complete_meeting as db_complete_meeting,
    get_meeting_stats as db_get_meeting_stats,
    test_automation_system as controller_test_automation
)

# 🔹 SCHEMAS
from schemas.meeting import MeetingCreate as DBCreateSchema, MeetingUpdate as DBUpdateSchema

# 🔹 AUTOMAÇÃO / EVENTOS
from core.events.activity_log import ActivityEvent
from db.repositories.activity_log_repository import ActivityLogRepository

# 🔹 ALERTAS
from core.alerts.alert_engine import AlertEngine

# 🔹 AUTOMAÇÃO COMPLETA
import asyncio

router = APIRouter(prefix="/meetings", tags=["Meetings"])

# =====================================================
# 🔓 ROTA PÚBLICA PARA REGISTRO NO SWAGGER
# (não exige autenticação)
# =====================================================
@router.get("/health")
def meetings_health():
    """Health check para o módulo de meetings"""
    return {
        "status": "healthy",
        "service": "meetings",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "2.0.0"
    }


# ==========================
# 🔹 UTIL — LOG DE EVENTOS (SAFE)
# ==========================
def log_event_safe(db: Session, event: ActivityEvent):
    """
    Registra evento sem quebrar o fluxo principal
    """
    try:
        repo = ActivityLogRepository(db)
        # como estamos em rota sync, chamamos o método async via loop
        asyncio.create_task(repo.save(event))
    except Exception as e:
        print(f"[WARN] Falha ao registrar evento: {e}")


# ==========================
# SCHEMAS LOCAIS (para compatibilidade)
# ==========================
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
# ROTAS PRINCIPAIS
# ==========================

@router.get("/", response_model=List[MeetingResponse])
def get_user_meetings(
    skip: int = 0,
    limit: int = 100,
    status: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_any_auth)
):
    """Listar reuniões do usuário autenticado"""
    user_id = current_user.get("user_id")
    if not user_id:
        raise HTTPException(status_code=401, detail="Usuário não autenticado")
    
    meetings = db_get_meetings(db, user_id=user_id, skip=skip, limit=limit, status=status)
    return meetings


@router.post("/", response_model=MeetingResponse, status_code=status.HTTP_201_CREATED)
def create_new_meeting(
    meeting: DBCreateSchema,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_any_auth)
):
    """Criar nova reunião"""
    user_id = current_user.get("user_id")
    if not user_id:
        raise HTTPException(status_code=401, detail="Usuário não autenticado")
    
    # Usa o controller real do banco de dados
    new_meeting = db_create_meeting(db, meeting, user_id)

    # 🔹 EVENTO: reunião criada
    log_event_safe(
        db,
        ActivityEvent(
            type="meeting.created",
            entity="meeting",
            entity_id=str(new_meeting.id),
            actor=str(user_id),
            payload={
                "title": new_meeting.title,
                "scheduled_time": new_meeting.scheduled_time.isoformat(),
                "participants": meeting.participants or []
            }
        )
    )

    # 🔔 ALERT ENGINE: alertas inteligentes
    try:
        alert_engine = AlertEngine(db)

        # 🔔 ALERTA: reunião sem participantes
        if not meeting.participants:
            alert_engine.emit(
                type="meeting.no_participants",
                severity="warning",
                title="Reunião criada sem participantes",
                message=f"A reunião '{new_meeting.title}' foi criada sem participantes.",
                entity="meeting",
                entity_id=str(new_meeting.id),
                actor=str(user_id),
            )

        # ⏰ ALERTA: reunião muito próxima do horário atual
        now = datetime.utcnow()
        scheduled = new_meeting.scheduled_time

        if scheduled <= now:
            alert_engine.emit(
                type="meeting.invalid_schedule",
                severity="critical",
                title="Reunião criada no passado",
                message=f"A reunião '{new_meeting.title}' foi criada com horário inválido.",
                entity="meeting",
                entity_id=str(new_meeting.id),
                actor=str(user_id),
            )
    except Exception as e:
        print(f"[Alerts] Erro ao emitir alertas: {e}")

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
    
    meeting = db_get_meeting(db, meeting_id)
    if not meeting:
        raise HTTPException(status_code=404, detail="Reunião não encontrada")
    
    # Verifica se o usuário tem acesso
    if meeting.organizer_id != user_id and user_id not in [p.user_id for p in meeting.participants]:
        raise HTTPException(status_code=403, detail="Acesso não autorizado")
    
    return meeting


@router.put("/{meeting_id}", response_model=MeetingResponse)
def update_existing_meeting(
    meeting_id: int,
    meeting: DBUpdateSchema,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_any_auth)
):
    """Atualizar reunião"""
    user_id = current_user.get("user_id")
    if not user_id:
        raise HTTPException(status_code=401, detail="Usuário não autenticado")
    
    # Verifica se a reunião existe e se o usuário é o organizador
    existing_meeting = db_get_meeting(db, meeting_id)
    if not existing_meeting:
        raise HTTPException(status_code=404, detail="Reunião não encontrada")
    
    if existing_meeting.organizer_id != user_id:
        raise HTTPException(status_code=403, detail="Apenas o organizador pode atualizar a reunião")
    
    updated = db_update_meeting(db, meeting_id, meeting)
    if not updated:
        raise HTTPException(status_code=404, detail="Reunião não encontrada")

    # 🔹 EVENTO: reunião atualizada
    log_event_safe(
        db,
        ActivityEvent(
            type="meeting.updated",
            entity="meeting",
            entity_id=str(updated.id),
            actor=str(user_id),
            payload={
                "updated_fields": list(meeting.model_dump(exclude_unset=True).keys())
            }
        )
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
    
    # Verifica se a reunião existe e se o usuário é o organizador
    existing_meeting = db_get_meeting(db, meeting_id)
    if not existing_meeting:
        raise HTTPException(status_code=404, detail="Reunião não encontrada")
    
    if existing_meeting.organizer_id != user_id:
        raise HTTPException(status_code=403, detail="Apenas o organizador pode deletar a reunião")
    
    success = db_delete_meeting(db, meeting_id)
    if not success:
        raise HTTPException(status_code=404, detail="Reunião não encontrada")
    
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
    
    # Verifica se a reunião existe e se o usuário é o organizador
    existing_meeting = db_get_meeting(db, meeting_id)
    if not existing_meeting:
        raise HTTPException(status_code=404, detail="Reunião não encontrada")
    
    if existing_meeting.organizer_id != user_id:
        raise HTTPException(status_code=403, detail="Apenas o organizador pode iniciar a reunião")
    
    started = db_start_meeting(db, meeting_id)
    if not started:
        raise HTTPException(status_code=404, detail="Reunião não encontrada")

    # 🔹 EVENTO: reunião iniciada
    log_event_safe(
        db,
        ActivityEvent(
            type="meeting.started",
            entity="meeting",
            entity_id=str(started.id),
            actor=str(user_id),
            payload={
                "started_at": started.started_at.isoformat() if started.started_at else None
            }
        )
    )

    # 🔔 ALERT ENGINE: alertas inteligentes
    try:
        alert_engine = AlertEngine(db)
        scheduled = started.scheduled_time
        started_at = started.started_at

        if scheduled and started_at and started_at > scheduled:
            alert_engine.emit(
                type="meeting.started_late",
                severity="info",
                title="Reunião iniciada com atraso",
                message=f"A reunião '{started.title}' foi iniciada após o horário agendado.",
                entity="meeting",
                entity_id=str(started.id),
                actor=str(user_id),
            )
    except Exception as e:
        print(f"[Alerts] Erro ao emitir alerta: {e}")

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
    
    # Verifica se a reunião existe e se o usuário é o organizador
    existing_meeting = db_get_meeting(db, meeting_id)
    if not existing_meeting:
        raise HTTPException(status_code=404, detail="Reunião não encontrada")
    
    if existing_meeting.organizer_id != user_id:
        raise HTTPException(status_code=403, detail="Apenas o organizador pode concluir a reunião")
    
    completed = db_complete_meeting(db, meeting_id)
    if not completed:
        raise HTTPException(status_code=404, detail="Reunião não encontrada")

    # 🔹 EVENTO: reunião concluída
    log_event_safe(
        db,
        ActivityEvent(
            type="meeting.completed",
            entity="meeting",
            entity_id=str(completed.id),
            actor=str(user_id),
            payload={
                "completed_at": completed.completed_at.isoformat() if completed.completed_at else None
            }
        )
    )

    # 🔔 ALERT ENGINE: alertas inteligentes
    try:
        alert_engine = AlertEngine(db)

        if not completed.started_at:
            alert_engine.emit(
                type="meeting.completed_without_start",
                severity="warning",
                title="Reunião concluída sem início",
                message=f"A reunião '{completed.title}' foi concluída sem ter sido iniciada.",
                entity="meeting",
                entity_id=str(completed.id),
                actor=str(user_id),
            )
    except Exception as e:
        print(f"[Alerts] Erro ao emitir alerta: {e}")

    # 🚀 AUTOMAÇÃO: Tenta disparar orquestração em background
    try:
        from core.orchestrator.automation_orchestrator import AutomationOrchestrator
        orchestrator = AutomationOrchestrator(db)
        asyncio.create_task(
            orchestrator.process_meeting_completion(completed)
        )
        print(f"[Automation] Automação disparada para reunião {completed.id}")
    except ImportError:
        print("[Automation] Módulo de automação não encontrado")
    except Exception as e:
        print(f"[Automation] Erro ao disparar automação: {e}")

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
    
    meeting = db_get_meeting(db, meeting_id)
    if not meeting:
        raise HTTPException(status_code=404, detail="Reunião não encontrada")
    
    # Verifica acesso
    if meeting.organizer_id != user_id and user_id not in [p.user_id for p in meeting.participants]:
        raise HTTPException(status_code=403, detail="Acesso não autorizado")
    
    participants = [p.user_id for p in meeting.participants]
    
    return {
        "meeting_id": meeting_id,
        "title": meeting.title,
        "participants": participants,
        "total_participants": len(participants)
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
    
    stats = db_get_meeting_stats(db, user_id)
    
    return {
        "scheduled": stats["scheduled"],
        "in_progress": stats["in_progress"],
        "completed": stats["completed"],
        "next_meeting": {
            "id": stats["next_meeting"],
            "scheduled_time": stats["next_meeting_time"]
        } if stats["next_meeting"] else None
    }


@router.get("/health")
def meetings_health():
    """Health check para o módulo de meetings"""
    return {
        "status": "healthy",
        "service": "meetings",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "2.0.0"
    }


# ==========================
# 🔥 ROTA DE TESTE DE AUTOMAÇÃO
# ==========================

@router.post("/test/automation")
async def test_automation_endpoint(
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_any_auth)
):
    """
    Endpoint para testar todo o sistema de automação
    Cria uma reunião, a conclui e dispara automações
    """
    print("\n" + "="*60)
    print("🚀 TESTE DO SISTEMA MAWDSLEYS - ENDPOINT")
    print("="*60)
    
    try:
        user_id = current_user.get("user_id") or 1
        
        # Usa a função de teste do controller
        result = controller_test_automation(db, user_id)
        
        print("="*60)
        print("🎯 TESTE VIA ENDPOINT COMPLETO!")
        print("="*60)
        
        return {
            "status": "success",
            "message": "Teste de automação executado com sucesso",
            "test_type": "full_automation_pipeline",
            "user_id": user_id,
            "result": result,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        print(f"❌ ERRO NO TESTE DO ENDPOINT: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=f"Erro no teste de automação: {str(e)}"
        )