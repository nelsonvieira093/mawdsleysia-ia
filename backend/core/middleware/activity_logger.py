# E:\MAWDSLEYS-AGENTE\backend\core\middleware\activity_logger.py
import time
import os
import asyncio
from typing import Optional

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
from sqlalchemy.orm import Session

from core.events.activity_log import ActivityEvent
from db.repositories.activity_log_repository import ActivityLogRepository
from database.session import SessionLocal

class ActivityLogMiddleware(BaseHTTPMiddleware):
    """Middleware global para registro automático de eventos"""
    
    def __init__(self, app: ASGIApp):
        super().__init__(app)
    
    async def dispatch(self, request: Request, call_next):
        # Início da request
        start_time = time.time()
        
        # Cria sessão do DB
        db = SessionLocal()
        request.state.db = db
        request.state.user_id = None
        
        try:
            # Extrair user_id do token
            user_id = await self._extract_user_id(request)
            request.state.user_id = user_id
            
            # Processa a request
            response = await call_next(request)
            
            # Calcula tempo de resposta
            process_time = time.time() - start_time
            
            # Registra evento
            if self._should_log_request(request, response.status_code):
                await self._log_event_async(
                    request=request,
                    response=response,
                    process_time=process_time,
                    user_id=user_id,
                    db=db
                )
            
            return response
            
        except Exception as e:
            # Log de erro
            await self._log_error_async(request, str(e), user_id, db)
            raise
            
        finally:
            # Fecha conexão com DB
            db.close()
    
    async def _extract_user_id(self, request: Request) -> Optional[str]:
        """Extrai user_id do token de autenticação"""
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            try:
                token = auth_header.replace("Bearer ", "")
                
                # Tenta decodificar JWT
                try:
                    from api.routes.auth import decode_token
                    payload = decode_token(token)
                    if payload and "user_id" in payload:
                        return str(payload["user_id"])
                except (ImportError, Exception):
                    pass
                
                # Fallback para desenvolvimento
                if "_" in token:
                    parts = token.split("_")
                    if len(parts) > 1 and parts[-1].isdigit():
                        return f"user_{parts[-1]}"
                        
            except Exception as e:
                print(f"[Middleware] Erro ao decodificar token: {e}")
        
        return None
    
    def _should_log_request(self, request: Request, status_code: int) -> bool:
        """Define quais requests devem ser logadas"""
        excluded_paths = [
            "/health", 
            "/metrics",
            "/docs",
            "/redoc",
            "/openapi.json",
            "/favicon.ico",
            "/static/",
            "/assets/",
            "/api/v1/chat/health",
        ]
        
        path = request.url.path
        
        # Não loga requisições excluídas
        if any(path.startswith(excluded) for excluded in excluded_paths):
            return False
        
        # Não loga OPTIONS (CORS preflight)
        if request.method == "OPTIONS":
            return False
        
        # Loga métodos HTTP importantes
        return request.method in ["GET", "POST", "PUT", "DELETE", "PATCH"]
    
    async def _log_event_async(self, request: Request, response: Response, 
                              process_time: float, user_id: Optional[str], db: Session):
        """Registra evento de forma assíncrona"""
        try:
            # Prepara payload do evento
            payload = {
                "method": request.method,
                "path": request.url.path,
                "status_code": response.status_code,
                "response_time_ms": round(process_time * 1000, 2),
                "query_params": dict(request.query_params),
                "user_agent": request.headers.get("user-agent", ""),
                "ip_address": request.client.host if request.client else None,
                "timestamp": time.time(),
            }
            
            if user_id:
                payload["user_id"] = user_id
            
            # Tenta pegar ID da entidade da URL
            path_parts = request.url.path.strip("/").split("/")
            if len(path_parts) >= 2 and path_parts[-1].isdigit():
                payload["entity_id"] = path_parts[-1]
            
            # Determina tipo de evento
            event_type = f"api.{request.method.lower()}"
            if "meetings" in request.url.path:
                event_type = f"meeting.{request.method.lower()}"
            elif "chat" in request.url.path:
                event_type = f"chat.{request.method.lower()}"
            
            # Cria evento
            event = ActivityEvent(
                type=event_type,
                entity="http_request",
                entity_id=f"{request.method}:{request.url.path}:{int(time.time())}",
                actor=user_id or "anonymous",
                payload=payload
            )
            
            # 1. Registra no Activity Log
            repo = ActivityLogRepository(db)
            await repo.save(event)
            
            # 2. 🔥 PROCESSAMENTO AUTOMÁTICO (INTEGRAÇÃO COM SEU EVENTPROCESSOR)
            await self._trigger_automated_processing(event, db)
            
            # Log para debug
            if os.getenv("ENVIRONMENT") == "development":
                print(f"[ActivityLogMiddleware] Evento registrado: {event_type} {request.url.path} - {response.status_code}")
            
        except Exception as e:
            print(f"[ActivityLogMiddleware] Erro ao registrar evento: {e}")
    
    async def _trigger_automated_processing(self, event: ActivityEvent, db: Session):
        """Dispara o processamento automático do evento usando SEU EventProcessor"""
        try:
            # ✅ USA O SEU EVENTPROCESSOR EXISTENTE
            from core.automation.event_processor import EventProcessor
            
            processor = EventProcessor(db)
            
            # Executa em background (não bloqueia)
            asyncio.create_task(processor.process_event(event))
            
            if os.getenv("ENVIRONMENT") == "development":
                print(f"[Middleware] ✅ Evento enviado para EventProcessor: {event.type}")
                
        except ImportError:
            # Se não encontrar, apenas avisa
            if os.getenv("ENVIRONMENT") == "development":
                print(f"[Middleware] ⚠️ EventProcessor não encontrado em core.automation")
        except Exception as e:
            print(f"[Middleware] ⚠️ Erro no EventProcessor: {e}")
    
    async def _log_error_async(self, request: Request, error_message: str, 
                              user_id: Optional[str], db: Session):
        """Registra erros de forma assíncrona"""
        try:
            event = ActivityEvent(
                type="api.error",
                entity="http_request",
                entity_id=f"error:{request.method}:{request.url.path}:{int(time.time())}",
                actor=user_id or "anonymous",
                payload={
                    "method": request.method,
                    "path": request.url.path,
                    "error": error_message,
                    "ip_address": request.client.host if request.client else None,
                    "timestamp": time.time(),
                }
            )
            
            repo = ActivityLogRepository(db)
            await repo.save(event)
            
            # Também processa erros automaticamente
            await self._trigger_automated_processing(event, db)
            
        except Exception as e:
            print(f"[ActivityLogMiddleware] Erro ao registrar erro: {e}")

# Função auxiliar
def get_db_from_request(request: Request) -> Session:
    """Retorna a sessão do DB injetada pelo middleware"""
    if hasattr(request.state, 'db'):
        return request.state.db
    else:
        return SessionLocal()