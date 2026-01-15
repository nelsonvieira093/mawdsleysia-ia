# backend/core/orchestrator/automation_orchestrator.py
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import asyncio

from core.memory.memory_engine import MemoryEngine
from core.alerts.alert_engine import AlertEngine
from core.events.activity_log import ActivityEvent
from db.repositories.activity_log_repository import ActivityLogRepository

class AutomationOrchestrator:
    """Orquestrador de automações do MAWDSLEYS"""
    
    def __init__(self, db: Session):
        self.db = db
        self.memory_engine = MemoryEngine(db)
        self.alert_engine = AlertEngine(db)
        self.activity_repo = ActivityLogRepository(db)
    
    async def process_meeting_completion(self, meeting_data: Dict[str, Any]):
        """
        Automação completa: Reunião concluída → Verifica ata → Alerta → Follow-up
        """
        user_id = meeting_data.get("organizer_id")
        meeting_id = meeting_data.get("id")
        meeting_title = meeting_data.get("title", "Reunião sem título")
        
        # 1. CONSULTA MEMÓRIA: Verifica se há ata registrada
        has_minutes = self._check_meeting_minutes(meeting_id)
        
        # 2. DECISÃO: Se não tem ata, dispara alerta
        if not has_minutes:
            await self._trigger_no_minutes_alert(
                user_id=user_id,
                meeting_id=meeting_id,
                meeting_title=meeting_title
            )
            
            # 3. AÇÃO: Cria follow-up automático
            await self._create_follow_up_task(
                user_id=user_id,
                meeting_id=meeting_id,
                meeting_title=meeting_title
            )
            
            # 4. REGISTRA NA MEMÓRIA
            self._record_automation_memory(
                user_id=user_id,
                meeting_id=meeting_id,
                action="automation_triggered"
            )
    
    def _check_meeting_minutes(self, meeting_id: int) -> bool:
        """Verifica se a reunião tem ata registrada"""
        # Consulta memórias relacionadas à reunião
        memories = self.memory_engine.search(
            query="minutes ata registro",
            entity_types=["meeting_minutes"],
            entity_id=str(meeting_id),
            limit=1
        )
        
        return len(memories) > 0
    
    async def _trigger_no_minutes_alert(self, user_id: int, meeting_id: int, meeting_title: str):
        """Dispara alerta sobre falta de ata"""
        self.alert_engine.emit(
            type="meeting.no_minutes",
            severity="warning",
            title="Reunião concluída sem ata",
            message=f"A reunião '{meeting_title}' foi concluída sem registro de ata. Crie o follow-up.",
            entity="meeting",
            entity_id=str(meeting_id),
            actor=str(user_id),
            metadata={
                "meeting_title": meeting_title,
                "suggested_action": "Criar ata da reunião"
            }
        )
        
        # Registra evento
        event = ActivityEvent(
            type="automation.alert_triggered",
            entity="meeting",
            entity_id=str(meeting_id),
            actor=str(user_id),
            payload={
                "alert_type": "no_minutes",
                "meeting_title": meeting_title,
                "timestamp": datetime.utcnow().isoformat()
            }
        )
        await self.activity_repo.save(event)
    
    async def _create_follow_up_task(self, user_id: int, meeting_id: int, meeting_title: str):
        """Cria tarefa de follow-up automática"""
        # TODO: Integrar com seu sistema de tasks/follow-ups
        
        # Por enquanto, registra na memória
        self.memory_engine.add_memory(
            user_id=user_id,
            entity_type="follow_up_task",
            entity_id=f"auto_followup_{meeting_id}",
            content=f"Follow-up automático para reunião: {meeting_title}",
            metadata={
                "automated": True,
                "meeting_id": meeting_id,
                "due_date": (datetime.utcnow() + timedelta(days=1)).isoformat(),
                "priority": "medium"
            }
        )
    
    def _record_automation_memory(self, user_id: int, meeting_id: int, action: str):
        """Registra execução da automação na memória"""
        self.memory_engine.add_memory(
            user_id=user_id,
            entity_type="automation_log",
            entity_id=f"auto_{meeting_id}_{datetime.utcnow().timestamp()}",
            content=f"Automação executada: {action} para reunião {meeting_id}",
            metadata={
                "action": action,
                "timestamp": datetime.utcnow().isoformat(),
                "status": "completed"
            }
        )
    
    async def run_scheduled_checks(self):
        """Executa verificações agendadas"""
        # Verifica reuniões que terminaram recentemente sem follow-up
        # (Implementar baseado no seu banco real)
        pass

# Singleton global (opcional)
_orchestrator_instance = None

def get_orchestrator(db: Session) -> AutomationOrchestrator:
    """Retorna instância do orquestrador"""
    global _orchestrator_instance
    if _orchestrator_instance is None:
        _orchestrator_instance = AutomationOrchestrator(db)
    return _orchestrator_instance