# E:\MAWDSLEYS-AGENTE\backend\api\routes\deliverables.py
from fastapi import APIRouter, Depends
from datetime import datetime, timedelta

# ✅ CORREÇÃO: Use require_any_auth que EXISTE no seu auth.py
from .auth import require_any_auth

router = APIRouter(prefix="/deliverables", tags=["Deliverables"])

@router.get("/")
async def get_deliverables(current_user = Depends(require_any_auth)):
    """Lista de entregáveis"""
    # Para debug
    user_id = current_user.get('user_id', 1)
    user_email = current_user.get('email', 'user@example.com')
    print(f"📦 Deliverables acessado por: {user_email} (ID: {user_id})")
    
    # Dados de exemplo
    deliverables = [
        {
            "id": 1,
            "title": "Relatório Mensal de Performance",
            "description": "Análise completa das métricas e KPIs do mês",
            "status": "pending",
            "priority": "high",
            "due_date": (datetime.now() + timedelta(days=3)).strftime("%Y-%m-%d"),
            "owner": current_user.get('name', 'Usuário'),
            "owner_id": user_id,
            "progress": 30,
            "tags": ["report", "kpi", "monthly"]
        },
        {
            "id": 2,
            "title": "Apresentação para Revisão de Cliente",
            "description": "Deck de apresentação dos resultados do projeto",
            "status": "in_progress",
            "priority": "medium",
            "due_date": (datetime.now() + timedelta(days=5)).strftime("%Y-%m-%d"),
            "owner": current_user.get('name', 'Usuário'),
            "owner_id": user_id,
            "progress": 65,
            "tags": ["presentation", "client", "review"]
        },
        {
            "id": 3,
            "title": "Documentação Técnica da API",
            "description": "Documentação completa dos endpoints e integrações",
            "status": "completed",
            "priority": "low",
            "due_date": (datetime.now() - timedelta(days=2)).strftime("%Y-%m-%d"),
            "owner": current_user.get('name', 'Usuário'),
            "owner_id": user_id,
            "progress": 100,
            "tags": ["documentation", "api", "technical"]
        },
        {
            "id": 4,
            "title": "Plano de Implementação Fase 2",
            "description": "Detalhamento das próximas funcionalidades",
            "status": "pending",
            "priority": "medium",
            "due_date": (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d"),
            "owner": current_user.get('name', 'Usuário'),
            "owner_id": user_id,
            "progress": 10,
            "tags": ["planning", "roadmap", "implementation"]
        }
    ]
    
    return deliverables