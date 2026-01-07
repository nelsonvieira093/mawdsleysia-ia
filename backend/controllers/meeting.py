# backend/controllers/meeting.py

from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import List, Optional, Dict, Any
from datetime import datetime

from models.meeting import Meeting, MeetingParticipant
from schemas.meeting import MeetingCreate, MeetingUpdate

# 🔹 AUTOMAÇÃO / EVENTOS
from core.events.activity_log import ActivityEvent
from db.repositories.activity_log_repository import ActivityLogRepository


# ===============================
# UTIL: registrar evento (safe)
# ===============================
def log_event_safe(db: Session, event: ActivityEvent):
    """
    Registra evento sem quebrar o fluxo principal
    """
    try:
        repo = ActivityLogRepository(db)
        repo.save_sync(event)   # 🔥 síncrono, seguro
    except Exception as e:
        print(f"[WARN] Falha ao registrar evento: {e}")


# ===============================
# CRUD REUNIÕES
# ===============================

def get_meeting(db: Session, meeting_id: int) -> Optional[Meeting]:
    """Busca uma reunião pelo ID"""
    return db.query(Meeting).filter(Meeting.id == meeting_id).first()


def get_meetings(
    db: Session,
    user_id: int,
    skip: int = 0,
    limit: int = 100,
    status: Optional[str] = None
) -> List[Meeting]:
    """Busca reuniões de um usuário"""
    query = db.query(Meeting).filter(
        (Meeting.organizer_id == user_id) |
        (Meeting.participants.any(user_id=user_id))
    )

    if status:
        query = query.filter(Meeting.status == status)

    return query.order_by(desc(Meeting.scheduled_time)).offset(skip).limit(limit).all()


def create_meeting(db: Session, meeting: MeetingCreate, organizer_id: int) -> Meeting:
    """Cria uma nova reunião"""
    db_meeting = Meeting(
        title=meeting.title,
        description=meeting.description,
        scheduled_time=meeting.scheduled_time,
        duration_minutes=meeting.duration_minutes,
        location=meeting.location,
        status="scheduled",
        organizer_id=organizer_id,
        agenda=meeting.agenda
    )

    db.add(db_meeting)
    db.commit()
    db.refresh(db_meeting)

    # Adiciona participantes
    if meeting.participants:
        for participant_id in meeting.participants:
            participant = MeetingParticipant(
                meeting_id=db_meeting.id,
                user_id=participant_id,
                status="invited"
            )
            db.add(participant)

    db.commit()

    # 🔹 EVENTO: reunião criada
    log_event_safe(
        db,
        ActivityEvent(
            type="meeting.created",
            entity="meeting",
            entity_id=str(db_meeting.id),
            actor=str(organizer_id),
            payload={
                "title": db_meeting.title,
                "scheduled_time": db_meeting.scheduled_time.isoformat(),
                "participants": meeting.participants or []
            }
        )
    )

    return db_meeting


def update_meeting(db: Session, meeting_id: int, meeting: MeetingUpdate) -> Optional[Meeting]:
    """Atualiza uma reunião existente"""
    db_meeting = get_meeting(db, meeting_id)
    if not db_meeting:
        return None

    update_data = meeting.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(db_meeting, field, value)

    db_meeting.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(db_meeting)

    # 🔹 EVENTO: reunião atualizada
    log_event_safe(
        db,
        ActivityEvent(
            type="meeting.updated",
            entity="meeting",
            entity_id=str(db_meeting.id),
            actor="system",
            payload={
                "updated_fields": list(update_data.keys())
            }
        )
    )

    return db_meeting


def delete_meeting(db: Session, meeting_id: int) -> bool:
    """Deleta uma reunião (soft delete)"""
    db_meeting = get_meeting(db, meeting_id)
    if not db_meeting:
        return False

    db_meeting.status = "cancelled"
    db.commit()

    # 🔹 EVENTO: reunião cancelada
    log_event_safe(
        db,
        ActivityEvent(
            type="meeting.cancelled",
            entity="meeting",
            entity_id=str(db_meeting.id),
            actor="system",
            payload={}
        )
    )

    return True


def start_meeting(db: Session, meeting_id: int) -> Optional[Meeting]:
    """Inicia uma reunião"""
    db_meeting = get_meeting(db, meeting_id)
    if not db_meeting:
        return None

    db_meeting.status = "in_progress"
    db_meeting.started_at = datetime.utcnow()
    db_meeting.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(db_meeting)

    # 🔹 EVENTO: reunião iniciada
    log_event_safe(
        db,
        ActivityEvent(
            type="meeting.started",
            entity="meeting",
            entity_id=str(db_meeting.id),
            actor="system",
            payload={
                "started_at": db_meeting.started_at.isoformat()
            }
        )
    )

    return db_meeting


def complete_meeting(db: Session, meeting_id: int) -> Optional[Meeting]:
    """Marca uma reunião como concluída"""
    db_meeting = get_meeting(db, meeting_id)
    if not db_meeting:
        return None

    db_meeting.status = "completed"
    db_meeting.completed_at = datetime.utcnow()
    db_meeting.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(db_meeting)

    # 🔹 EVENTO: reunião concluída
    log_event_safe(
        db,
        ActivityEvent(
            type="meeting.completed",
            entity="meeting",
            entity_id=str(db_meeting.id),
            actor="system",
            payload={
                "completed_at": db_meeting.completed_at.isoformat()
            }
        )
    )

    return db_meeting


def get_meeting_stats(db: Session, user_id: int) -> Dict[str, Any]:
    """Retorna estatísticas de reuniões"""
    scheduled = db.query(Meeting).filter(
        Meeting.organizer_id == user_id,
        Meeting.status == "scheduled"
    ).count()

    in_progress = db.query(Meeting).filter(
        Meeting.organizer_id == user_id,
        Meeting.status == "in_progress"
    ).count()

    completed = db.query(Meeting).filter(
        Meeting.organizer_id == user_id,
        Meeting.status == "completed"
    ).count()

    next_meeting = db.query(Meeting).filter(
        Meeting.organizer_id == user_id,
        Meeting.status == "scheduled",
        Meeting.scheduled_time >= datetime.utcnow()
    ).order_by(Meeting.scheduled_time).first()

    return {
        "scheduled": scheduled,
        "in_progress": in_progress,
        "completed": completed,
        "next_meeting": next_meeting.id if next_meeting else None,
        "next_meeting_time": next_meeting.scheduled_time if next_meeting else None
    }

# ===============================
# FUNÇÃO DE TESTE PARA AUTOMAÇÃO
# ===============================

def test_automation_system(db: Session, user_id: int = 1) -> Dict[str, Any]:
    """
    Testa todo o sistema de automação de reuniões.
    Esta função pode ser chamada por um endpoint ou script.
    """
    print("\n" + "="*60)
    print("🚀 TESTE DO SISTEMA MAWDSLEYS - CONTROLLER")
    print("="*60)
    
    try:
        # Importação local para evitar circular dependencies
        from schemas.meeting import MeetingCreate
        
        # 1. Cria reunião de teste
        meeting_data = MeetingCreate(
            title="🚀 TESTE DE AUTOMAÇÃO (Controller)",
            description="Reunião criada pelo controller para testar automações",
            scheduled_time=datetime.utcnow(),
            duration_minutes=30,
            location="Virtual",
            agenda="Testar sistema de automação",
            participants=[]
        )
        
        new_meeting = create_meeting(db, meeting_data, user_id)
        print(f"✅ 1. Reunião criada: ID {new_meeting.id} - '{new_meeting.title}'")
        
        # 2. Tenta registrar evento
        try:
            log_event_safe(
                db,
                ActivityEvent(
                    type="meeting.test.created",
                    entity="meeting",
                    entity_id=str(new_meeting.id),
                    actor=str(user_id),
                    payload={
                        "title": new_meeting.title,
                        "test": True,
                        "source": "controller_test"
                    }
                )
            )
            print("✅ 2. Evento registrado no activity log")
        except Exception as e:
            print(f"⚠️ 2. Erro ao registrar evento: {e}")
        
        # 3. Conclui reunião
        completed = complete_meeting(db, new_meeting.id)
        if completed:
            print(f"✅ 3. Reunião concluída: ID {completed.id}")
            
            # 4. Tenta disparar automação (se o módulo existir)
            try:
                # Importação condicional - só tenta se o módulo existir
                from core.orchestrator.automation_orchestrator import AutomationOrchestrator
                import asyncio
                
                orchestrator = AutomationOrchestrator(db)
                # Cria task async mas não espera (fire and forget)
                asyncio.create_task(orchestrator.process_meeting_completion(completed))
                print("✅ 4. Automação disparada em background")
            except ImportError:
                print("⚠️ 4. Módulo de automação não encontrado (pode ser normal)")
            except Exception as e:
                print(f"⚠️ 4. Erro na automação: {e}")
        else:
            print("❌ 3. Falha ao concluir reunião")
        
        print("="*60)
        print("🎯 TESTE DO CONTROLLER COMPLETO!")
        print("="*60)
        
        return {
            "status": "success",
            "test": "automation",
            "meeting_id": new_meeting.id,
            "meeting_title": new_meeting.title,
            "meeting_completed": bool(completed),
            "timestamp": datetime.utcnow().isoformat(),
            "source": "meeting_controller"
        }
        
    except Exception as e:
        print(f"❌ ERRO NO TESTE DO CONTROLLER: {e}")
        import traceback
        traceback.print_exc()
        raise