# E:\MAWDSLEYS-AGENTE\backend\api\routes\history.py
from fastapi import APIRouter, Depends
from datetime import datetime, timedelta

# ✅ CORREÇÃO: Use require_any_auth que EXISTE no seu auth.py
from .auth import require_any_auth

router = APIRouter(prefix="/history", tags=["History"])

@router.get("/")
async def get_history(current_user = Depends(require_any_auth)):
    """Histórico de atividades"""
    # Para debug
    user_id = current_user.get('user_id', 1)
    print(f"📊 Histórico acessado por usuário ID: {user_id}")
    
    # Cria histórico dos últimos 7 dias
    history = []
    today = datetime.now()
    
    for i in range(7):
        date = today - timedelta(days=i)
        history.append({
            "date": date.strftime("%Y-%m-%d"),
            "day_of_week": date.strftime("%A"),
            "user_id": user_id,
            "actions": [
                {
                    "type": "note_created",
                    "count": (i % 3) + 1,
                    "description": "Notas criadas no sistema"
                },
                {
                    "type": "meeting_scheduled", 
                    "count": (i % 2) + 1,
                    "description": "Reuniões agendadas"
                },
                {
                    "type": "followup_created",
                    "count": i % 4,
                    "description": "Follow-ups criados"
                }
            ],
            "total_actions": (i % 3) + (i % 2) + (i % 4) + 3
        })
    
    return history