# E:\MAWDSLEYS-AGENTE\backend\api\routes\followups.py
"""
FollowUp Routes (VERSÃO PRODUTO)
===============================

Responsável apenas por:
- HTTP
- Validação de entrada/saída
- Autenticação
- Códigos de erro

❌ NÃO contém regra de negócio
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from database.session import get_db
from api.routes.auth import require_any_auth
from controllers.followup_controller import FollowUpController
from schemas.followup import FollowUpCreate, FollowUpUpdate, FollowUpOut

router = APIRouter(prefix="/followups", tags=["FollowUps"])


# =========================================================
# 🔐 USER ID NORMALIZER (CRÍTICO)
# =========================================================
def get_user_id(user: dict) -> int:
    if "id" in user:
        return user["id"]
    if "user_id" in user:
        return user["user_id"]
    if "sub" in user:
        return int(user["sub"])

    raise HTTPException(
        status_code=401,
        detail="Token inválido: user_id não encontrado"
    )


# =========================================================
# 🔹 CREATE (MANTÉM PROTEÇÃO)
# =========================================================
@router.post("/", response_model=FollowUpOut)
def create_followup(
    payload: FollowUpCreate,
    db: Session = Depends(get_db),
    user: dict = Depends(require_any_auth),
):
    user_id = get_user_id(user)

    return FollowUpController.create_followup(
        db=db,
        user_id=user_id,
        description=payload.description,
        title=payload.title,
        note_id=payload.note_id,
        due_date=payload.due_date,
        priority=payload.priority,
    )


# =========================================================
# 🔹 LIST (COM AUTENTICAÇÃO + CONTRATO PURO)
# =========================================================
@router.get("/", response_model=List[FollowUpOut])
def list_followups(
    db: Session = Depends(get_db),
    user: dict = Depends(require_any_auth),
):
    user_id = get_user_id(user)

    followups = FollowUpController.list_followups(
        db=db,
        user_id=user_id,
    )

    # ⚠️ CONTRATO DEFINITIVO:
    # Retorna APENAS uma lista (array JSON)
    return followups


# =========================================================
# 🔹 GET (DETALHE) — MANTÉM PROTEÇÃO
# =========================================================
@router.get("/{followup_id}", response_model=FollowUpOut)
def get_followup(
    followup_id: int,
    db: Session = Depends(get_db),
    user: dict = Depends(require_any_auth),
):
    user_id = get_user_id(user)

    followup = FollowUpController.get_followup(
        db=db,
        followup_id=followup_id,
        user_id=user_id,
    )

    if not followup:
        raise HTTPException(status_code=404, detail="Follow-up não encontrado")

    return followup


# =========================================================
# 🔹 UPDATE — MANTÉM PROTEÇÃO
# =========================================================
@router.put("/{followup_id}", response_model=FollowUpOut)
def update_followup(
    followup_id: int,
    payload: FollowUpUpdate,
    db: Session = Depends(get_db),
    user: dict = Depends(require_any_auth),
):
    user_id = get_user_id(user)

    followup = FollowUpController.update_followup(
        db=db,
        followup_id=followup_id,
        user_id=user_id,
        title=payload.title,
        description=payload.description,
        due_date=payload.due_date,
        priority=payload.priority,
        status=payload.status,
    )

    if not followup:
        raise HTTPException(status_code=404, detail="Follow-up não encontrado")

    return followup


# =========================================================
# 🔹 CLOSE — MANTÉM PROTEÇÃO
# =========================================================
@router.post("/{followup_id}/close", response_model=FollowUpOut)
def close_followup(
    followup_id: int,
    db: Session = Depends(get_db),
    user: dict = Depends(require_any_auth),
):
    user_id = get_user_id(user)

    followup = FollowUpController.close_followup(
        db=db,
        followup_id=followup_id,
        user_id=user_id,
    )

    if not followup:
        raise HTTPException(status_code=404, detail="Follow-up não encontrado")

    return followup
