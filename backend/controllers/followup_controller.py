# backend/controllers/followup_controller.py

"""
FollowUp Controller (VERSÃO PRODUTO)
===================================

Responsável por:
- Orquestrar casos de uso de FollowUp
- Validar existência e ownership
- Delegar persistência ao Repository

❌ NÃO contém queries
❌ NÃO contém regras de automação
"""

from sqlalchemy.orm import Session
from typing import Optional
from uuid import UUID as UUIDType
from datetime import date

from db.repositories.followup_repository import FollowUpRepository
from models.followup import FollowUp


class FollowUpController:

    # =========================================================
    # 🔹 CREATE
    # =========================================================
    @staticmethod
    def create_followup(
        *,
        db: Session,
        user_id: int,
        description: str,
        title: Optional[str] = None,
        note_id: Optional[UUIDType] = None,
        due_date: Optional[date] = None,
        priority: str = "MEDIA",
    ) -> FollowUp:
        return FollowUpRepository.create(
            db,
            user_id=user_id,
            description=description,
            title=title,
            note_id=note_id,
            due_date=due_date,
            priority=priority,
        )

    # =========================================================
    # 🔹 LIST
    # =========================================================
    @staticmethod
    def list_user_followups(
        db: Session,
        *,
        user_id: int,
    ):
        return FollowUpRepository.list_by_user(
            db,
            user_id=user_id,
        )

    # =========================================================
    # 🔹 GET (DETALHE)
    # =========================================================
    @staticmethod
    def get_followup(
        *,
        db: Session,
        followup_id: int,
        user_id: int,
    ) -> Optional[FollowUp]:
        return FollowUpRepository.get_by_id(
            db,
            followup_id=followup_id,
            user_id=user_id,
        )


@staticmethod
def list_followups(db: Session, user_id: int):
    return (
        db.query(FollowUp)
        .filter(FollowUp.owner_id == user_id)
        .order_by(FollowUp.due_date.asc())
        .all()
    )

    # =========================================================
    # 🔹 UPDATE
    # =========================================================
    @staticmethod
    def update_followup(
        *,
        db: Session,
        followup_id: int,
        user_id: int,
        title: Optional[str] = None,
        description: Optional[str] = None,
        due_date: Optional[date] = None,
        priority: Optional[str] = None,
        status: Optional[str] = None,
    ) -> Optional[FollowUp]:
        followup = FollowUpRepository.get_by_id(
            db,
            followup_id=followup_id,
            user_id=user_id,
        )

        if not followup:
            return None

        # Atualizações pontuais (sem regra de negócio)
        if title is not None:
            followup.title = title

        if description is not None:
            followup.description = description

        if due_date is not None:
            followup.due_date = due_date

        if priority is not None:
            followup.priority = priority

        if status is not None:
            followup.status = status

        db.commit()
        db.refresh(followup)

        return followup

    # =========================================================
    # 🔹 CLOSE
    # =========================================================
    @staticmethod
    def close_followup(
        *,
        db: Session,
        followup_id: int,
        user_id: int,
    ) -> Optional[FollowUp]:
        return FollowUpRepository.close(
            db,
            followup_id=followup_id,
            user_id=user_id,
        )
