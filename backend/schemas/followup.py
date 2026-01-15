# backend/schemas/followup.py - VERSÃO CORRIGIDA

from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import date, datetime
from uuid import UUID
import enum


# Enum para status (opcional, mas recomendado)
class FollowUpStatus(str, enum.Enum):
    ABERTO = "ABERTO"
    EM_ANDAMENTO = "EM_ANDAMENTO"
    CONCLUIDO = "CONCLUIDO"


# =====================================================
# BASE (campos comuns - APENAS CAMPOS QUE EXISTEM NO BANCO)
# =====================================================
class FollowUpBase(BaseModel):
    description: str  # OBRIGATÓRIO no banco
    due_date: Optional[date] = None
    status: FollowUpStatus = FollowUpStatus.ABERTO  # Usar Enum
    
    # ⚠️ REMOVER: title, priority (não existem no banco)


# =====================================================
# CREATE
# =====================================================
class FollowUpCreate(FollowUpBase):
    note_id: Optional[UUID] = None
    owner_id: Optional[int] = None  # ⚠️ Mudar de user_id para owner_id


# =====================================================
# UPDATE
# =====================================================
class FollowUpUpdate(BaseModel):
    description: Optional[str] = None
    due_date: Optional[date] = None
    status: Optional[FollowUpStatus] = None
    note_id: Optional[UUID] = None


# =====================================================
# OUTPUT (ESQUEMA FINAL QUE CORRESPONDE AO BANCO)
# =====================================================
class FollowUpOut(BaseModel):
    # ⚠️ CORREÇÕES CRÍTICAS:
    id: UUID  # ⚠️ MUDAR: int → UUID
    owner_id: Optional[int] = None  # ⚠️ MUDAR: user_id → owner_id (e pode ser NULL)
    
    # Campos do FollowUpBase
    description: str
    due_date: Optional[date] = None
    status: FollowUpStatus
    
    # Campos adicionais
    note_id: Optional[UUID] = None
    ritual_id: Optional[UUID] = None  # Se existir no banco
    source_note_id: Optional[UUID] = None  # Se existir no banco
    created_at: Optional[datetime] = None
    
    # ⚠️ REMOVER: title, priority, user_id, updated_at
    
    # Config Pydantic v2
    model_config = ConfigDict(
        from_attributes=True,  # Substitui orm_mode no Pydantic v2
        use_enum_values=True  # Para usar valores do Enum
    )