import time
import os
import asyncio
from typing import Optional

from fastapi import Request
from sqlalchemy.orm import Session

from core.events.activity_log import ActivityEvent
from db.repositories.activity_log_repository import ActivityLogRepository
from database.session import SessionLocal


# =========================================================
# MIDDLEWARE FUNCIONAL (SAFE – NÃO QUEBRA BODY)
# =========================================================

async def activity_log_middleware(request: Request, call_next):
    """
    Middleware global para registro automático de eventos.
    ✔ NÃO consome body
    ✔ NÃO interfere no parsing
    ✔ Compatível com todo o backend atual
    """

    start_time = time.time()

    db: Session = SessionLocal()
    request.state.db = db
    request.state.user_id = None

    try:
        # Extrai user_id do header (se existir)
        user_id = _extract_user_id(request)
        request.state.user_id = user_id

        # Processa request normalmente
        response = await call_next(request)

        process_time = time.time() - start_time

        if _should_log_request(request):
            await _log_event_async(
                request=request,
                response=response,
                process_time=process_time,
                user_id=user_id,
                db=db,
            )

        return response

    except Exception as e:
        await _log_error_async(request, str(e), request.state.user_id, db)
        raise

    finally:
        db.close()


# =========================================================
# HELPERS
# =========================================================

def _extract_user_id(request: Request) -> Optional[str]:
    """Extrai user_id do token de autenticação"""
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        try:
            token = auth_header.replace("Bearer ", "")
            from api.routes.auth import decode_token
            payload = decode_token(token)
            if payload and "user_id" in payload:
                return str(payload["user_id"])
        except Exception:
            pass
    return None


def _should_log_request(request: Request) -> bool:
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

    if any(path.startswith(excluded) for excluded in excluded_paths):
        return False

    if request.method == "OPTIONS":
        return False

    return request.method in ["GET", "POST", "PUT", "DELETE", "PATCH"]


async def _log_event_async(
    request: Request,
    response,
    process_time: float,
    user_id: Optional[str],
    db: Session,
):
    try:
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

        event_type = f"api.{request.method.lower()}"
        if "meetings" in request.url.path:
            event_type = f"meeting.{request.method.lower()}"
        elif "chat" in request.url.path:
            event_type = f"chat.{request.method.lower()}"

        event = ActivityEvent(
            type=event_type,
            entity="http_request",
            entity_id=f"{request.method}:{request.url.path}:{int(time.time())}",
            actor=user_id or "anonymous",
            payload=payload,
        )

        repo = ActivityLogRepository(db)
        await repo.save(event)

        await _trigger_automated_processing(event, db)

        if os.getenv("ENVIRONMENT") == "development":
            print(f"[ActivityLog] {event_type} {request.url.path}")

    except Exception as e:
        print(f"[ActivityLogMiddleware] Erro ao registrar evento: {e}")


async def _trigger_automated_processing(event: ActivityEvent, db: Session):
    try:
        from core.automation.event_processor import EventProcessor
        processor = EventProcessor(db)
        asyncio.create_task(processor.process_event(event))
    except Exception as e:
        print(f"[ActivityLogMiddleware] ⚠️ EventProcessor erro: {e}")


async def _log_error_async(
    request: Request,
    error_message: str,
    user_id: Optional[str],
    db: Session,
):
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
                "timestamp": time.time(),
            },
        )

        repo = ActivityLogRepository(db)
        await repo.save(event)

        await _trigger_automated_processing(event, db)

    except Exception as e:
        print(f"[ActivityLogMiddleware] Erro ao registrar erro: {e}")


# =========================================================
# AUXILIAR
# =========================================================

def get_db_from_request(request: Request) -> Session:
    if hasattr(request.state, "db"):
        return request.state.db
    return SessionLocal()
