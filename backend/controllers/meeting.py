
#/e/MAWDSLEYS-AGENTE/backend/controllers/meeting.py << 'EOF'
# backend/controllers/meeting.py
from sqlalchemy.orm import Session
from sqlalchemy import desc, func
from typing import List, Optional, Dict, Any
from datetime import datetime

from models.meeting import Meeting, MeetingParticipant
from schemas.meeting import MeetingCreate, MeetingUpdate


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
    return db_meeting


def delete_meeting(db: Session, meeting_id: int) -> bool:
    """Deleta uma reunião (soft delete)"""
    db_meeting = get_meeting(db, meeting_id)
    if not db_meeting:
        return False
    
    db_meeting.status = "cancelled"
    db.commit()
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
    return db_meeting


def get_meeting_stats(db: Session, user_id: int) -> Dict[str, Any]:
    """Retorna estatísticas de reuniões"""
    # Reuniões agendadas
    scheduled = db.query(Meeting).filter(
        Meeting.organizer_id == user_id,
        Meeting.status == "scheduled"
    ).count()
    
    # Reuniões em andamento
    in_progress = db.query(Meeting).filter(
        Meeting.organizer_id == user_id,
        Meeting.status == "in_progress"
    ).count()
    
    # Reuniões concluídas
    completed = db.query(Meeting).filter(
        Meeting.organizer_id == user_id,
        Meeting.status == "completed"
    ).count()
    
    # Próxima reunião
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
