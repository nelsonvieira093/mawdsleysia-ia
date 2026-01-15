
#/e/MAWDSLEYS-AGENTE/backend/schemas/meeting.py << 'EOF'
# backend/schemas/meeting.py
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List, Dict, Any
from enum import Enum


class MeetingStatus(str, Enum):
    SCHEDULED = "scheduled"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class MeetingCreate(BaseModel):
    """Schema para criação de reunião"""
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    scheduled_time: datetime
    duration_minutes: int = Field(60, ge=15, le=480)  # 15min a 8h
    location: Optional[str] = Field(None, max_length=200)
    participants: Optional[List[int]] = Field(default_factory=list)
    agenda: Optional[str] = Field(None, max_length=2000)


class MeetingUpdate(BaseModel):
    """Schema para atualização de reunião"""
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    scheduled_time: Optional[datetime] = None
    duration_minutes: Optional[int] = Field(None, ge=15, le=480)
    location: Optional[str] = Field(None, max_length=200)
    status: Optional[MeetingStatus] = None
    agenda: Optional[str] = Field(None, max_length=2000)


class MeetingParticipantResponse(BaseModel):
    """Schema para resposta de participante"""
    user_id: int
    name: str
    email: str
    status: str  # invited, attending, declined
    joined_at: Optional[datetime] = None


class MeetingResponse(BaseModel):
    """Schema para resposta de reunião"""
    id: int
    title: str
    description: Optional[str]
    scheduled_time: datetime
    duration_minutes: int
    location: Optional[str]
    status: str
    organizer_id: int
    agenda: Optional[str]
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    participants: List[MeetingParticipantResponse] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class MeetingListResponse(BaseModel):
    """Schema para lista de reuniões"""
    items: List[MeetingResponse]
    total: int
    page: int
    size: int
    pages: int


class MeetingStats(BaseModel):
    """Estatísticas de reuniões"""
    scheduled: int
    in_progress: int
    completed: int
    next_meeting: Optional[int] = None
    next_meeting_time: Optional[datetime] = None
