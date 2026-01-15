from fastapi import APIRouter, Depends, Request
from typing import Dict, Any

from api.routes.auth import require_any_auth

router = APIRouter(
    prefix="/debug",
    tags=["Debug"]
)


@router.get("/routes")
def debug_routes(request: Request):
    """
    Lista todas as rotas registradas na aplicação
    (rota pública – usada para debug)
    """
    app = request.app  # ✅ pega a instância real do FastAPI

    routes_info = []

    for route in app.routes:
        methods = list(route.methods) if hasattr(route, "methods") else []
        routes_info.append({
            "path": route.path,
            "name": route.name,
            "methods": methods
        })

    return {
        "total_routes": len(routes_info),
        "routes": routes_info
    }


@router.get("/protected-test")
def protected_test(
    auth: Dict[str, Any] = Depends(require_any_auth)
):
    """
    Rota protegida para validar JWT na prática
    """
    return {
        "ok": True,
        "message": "Token válido ✅ acesso autorizado",
        "auth": auth
    }
