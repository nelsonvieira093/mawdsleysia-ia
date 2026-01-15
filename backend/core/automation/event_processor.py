# E:\MAWDSLEYS-AGENTE\backend\core\automation\event_processor.py
from sqlalchemy.orm import Session
from core.memory.memory_engine import MemoryEngine
from core.alerts.alert_engine import AlertEngine
from core.events.activity_log import ActivityEvent
import time

class EventProcessor:
    """Processa eventos e os converte em memória/alertas automaticamente"""
    
    def __init__(self, db: Session):
        self.db = db
        self.memory_engine = MemoryEngine(db)
        self.alert_engine = AlertEngine(db)
    
    async def process_event(self, event: ActivityEvent):
        """Converte evento em memória do agente e verifica alertas"""
        
        try:
            # 1️⃣ Converte actor para user_id válido
            user_id = self._extract_user_id(event.actor)
            
            # 2️⃣ Extrai conteúdo significativo do evento
            content = self._create_memory_content(event)
            
            # 3️⃣ Adiciona à memória do agente
            memory_id = None
            try:
                memory_id = self.memory_engine.add_memory(
                    user_id=user_id,
                    entity_type=event.entity,
                    entity_id=event.entity_id,
                    content=content,
                    metadata={
                        "event_type": event.type,
                        "original_payload": event.payload,
                        "processed": True,
                        "source": "activity_log_middleware",
                        "timestamp": event.payload.get('timestamp', time.time())
                    }
                )
            except AttributeError:
                print(f"[EventProcessor] ⚠️ MemoryEngine.add_memory não disponível")
                memory_id = "memory_disabled"
            
            # 4️⃣ Verifica se deve gerar alerta automático
            await self._check_for_automated_alerts(event)
            
            # Log de sucesso
            print(f"[EventProcessor] ✅ Evento {event.type} processado → Memória ID: {memory_id}")
            
            return memory_id
            
        except Exception as e:
            print(f"[EventProcessor] ❌ Erro ao processar evento: {e}")
            return None
    
    def _extract_user_id(self, actor: str) -> str:
        """Extrai user_id do actor do evento"""
        if not actor or actor == "anonymous":
            return "system"
        elif actor.startswith("user_"):
            return actor
        else:
            # Fallback para qualquer string como actor
            return f"user_{hash(actor) % 10000:04d}"
    
    def _create_memory_content(self, event: ActivityEvent) -> str:
        """Cria conteúdo descritivo para a memória"""
        
        # Para eventos HTTP
        if event.type.startswith("api."):
            method = event.payload.get('method', '?')
            path = event.payload.get('path', '?')
            status = event.payload.get('status_code', '?')
            response_time = event.payload.get('response_time_ms', 0)
            
            return f"HTTP {method} {path} - Status: {status} - Tempo: {response_time}ms"
        
        # Para eventos de meeting
        elif event.type.startswith("meeting."):
            action = event.type.split('.')[-1]
            title = event.payload.get('title', 'Sem título')
            
            if action == "created":
                return f"Reunião criada: '{title}'"
            elif action == "updated":
                return f"Reunião atualizada: '{title}'"
            elif action == "completed":
                return f"Reunião concluída: '{title}'"
            else:
                return f"Reunião {action}: '{title}'"
        
        # Para eventos de chat
        elif event.type.startswith("chat."):
            message = event.payload.get('message', '')[:100]
            return f"Chat: {message}..."
        
        # Para erros
        elif event.type == "api.error":
            error = event.payload.get('error', 'Erro desconhecido')
            path = event.payload.get('path', 'endpoint desconhecido')
            return f"Erro em {path}: {error}"
        
        # Padrão
        else:
            return f"Evento {event.type} processado"
    
    async def _check_for_automated_alerts(self, event: ActivityEvent):
        """Verifica regras para gerar alertas automáticos"""
        
        # ✅ CORREÇÃO: Todos os alert_engine.emit() agora têm AWAIT
        
        # Regra 1: Erros HTTP 5xx (erros de servidor)
        status_code = event.payload.get('status_code')
        if status_code and status_code >= 500:
            await self.alert_engine.emit(  # ✅ CORREÇÃO: Adicionado AWAIT
                type="system.api_error",
                severity="critical",
                title="🚨 Erro crítico na API",
                message=f"Erro {status_code} em {event.payload.get('path', 'endpoint')}",
                entity="system",
                entity_id=event.entity_id,
                actor="system_monitor",
                metadata={
                    "error_details": event.payload.get('error', 'Desconhecido'),
                    "user_agent": event.payload.get('user_agent', ''),
                    "timestamp": event.payload.get('timestamp')
                }
            )
        
        # Regra 2: Resposta muito lenta (> 5 segundos)
        response_time = event.payload.get('response_time_ms', 0)
        if response_time > 5000:  # 5 segundos
            await self.alert_engine.emit(  # ✅ CORREÇÃO: Adicionado AWAIT
                type="system.performance.slow",
                severity="warning",
                title="⚠️ Endpoint lento",
                message=f"{event.payload.get('path', 'Endpoint')} respondeu em {response_time}ms",
                entity="api_endpoint",
                entity_id=event.payload.get('path', 'unknown'),
                actor="performance_monitor",
                metadata={
                    "response_time": response_time,
                    "threshold": 5000
                }
            )
        
        # Regra 3: Muitos erros 4xx (client errors)
        if status_code and 400 <= status_code < 500:
            path = event.payload.get('path', '')
            if "auth" in path or "login" in path:
                await self.alert_engine.emit(  # ✅ CORREÇÃO: Adicionado AWAIT
                    type="security.auth_issues",
                    severity="warning",
                    title="🔐 Possível problema de autenticação",
                    message=f"Erro {status_code} em endpoint de autenticação",
                    entity="auth_system",
                    entity_id=path,
                    actor="security_monitor"
                )

# Singleton para uso fácil
_event_processor_instance = None

def get_event_processor(db: Session) -> EventProcessor:
    """Retorna instância do processador de eventos"""
    global _event_processor_instance
    if _event_processor_instance is None:
        _event_processor_instance = EventProcessor(db)
    return _event_processor_instance