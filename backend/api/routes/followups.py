# backend/api/routes/followups.py - VERSÃO CORRIGIDA
from  fastapi import APIRouter

router = APIRouter(prefix="/followups", tags=["FollowUps"])

@router.get("/")
def get_followups():
    return {"message": "FollowUps endpoint"}
