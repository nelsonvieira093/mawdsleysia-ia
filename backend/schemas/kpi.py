
# /e/MAWDSLEYS-AGENTE/backend/schemas/kpi.py << 
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List, Dict, Any
from enum import Enum


class KPIFrequency(str, Enum):
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    YEARLY = "yearly"


class KPICreate(BaseModel):
    """Schema para criação de KPI"""
    name: str = Field(..., min_length=1, max_length=200, description="Nome do KPI")
    description: Optional[str] = Field(None, max_length=1000, description="Descrição do KPI")
    target_value: float = Field(..., gt=0, description="Valor alvo do KPI")
    current_value: Optional[float] = Field(0.0, ge=0, description="Valor atual do KPI")
    unit: Optional[str] = Field("", max_length=50, description="Unidade de medida (%, R$, unidades, etc.)")
    frequency: KPIFrequency = Field(KPIFrequency.MONTHLY, description="Frequência de medição")
    department: Optional[str] = Field(None, max_length=100, description="Departamento responsável")
    category: Optional[str] = Field(None, max_length=100, description="Categoria do KPI")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Metadados adicionais")


class KPIUpdate(BaseModel):
    """Schema para atualização de KPI"""
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    target_value: Optional[float] = Field(None, gt=0)
    current_value: Optional[float] = Field(None, ge=0)
    unit: Optional[str] = Field(None, max_length=50)
    frequency: Optional[KPIFrequency] = None
    department: Optional[str] = Field(None, max_length=100)
    category: Optional[str] = Field(None, max_length=100)
    metadata: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None


class KPIResponse(BaseModel):
    """Schema para resposta de KPI"""
    id: int
    name: str
    description: Optional[str]
    target_value: float
    current_value: float
    unit: str
    frequency: str
    department: Optional[str]
    category: Optional[str]
    user_id: Optional[int]
    metadata: Optional[Dict[str, Any]]
    is_active: bool
    created_at: datetime
    updated_at: datetime
    progress_percentage: Optional[float] = None
    
    class Config:
        from_attributes = True


class KPIListResponse(BaseModel):
    """Schema para lista de KPIs"""
    items: List[KPIResponse]
    total: int
    page: int
    size: int
    pages: int


class KPIProgress(BaseModel):
    """Schema para progresso do KPI"""
    kpi_id: int
    current_value: float
    target_value: float
    progress_percentage: float
    status: str  # on_track, at_risk, off_track
    last_updated: datetime
    days_remaining: Optional[int] = None
    trend: Optional[str] = None  # up, down, stable


class KPIStats(BaseModel):
    """Estatísticas de KPIs"""
    total_kpis: int
    active_kpis: int
    average_progress: float
    on_track: int
    at_risk: int
    off_track: int
