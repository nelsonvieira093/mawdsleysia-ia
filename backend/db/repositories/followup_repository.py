# E:\MAWDSLEYS-AGENTE\backend\db\repositories\followup_repository.py
"""
FollowUp Repository (VERSÃO PRODUTO)
===================================

Responsável EXCLUSIVAMENTE por:
- Queries
- Persistência
- Filtros
- Ordenações
- Consultas reutilizáveis

❌ NÃO contém regras de negócio
❌ NÃO decide prioridade
❌ NÃO cria follow-up automaticamente

Esse arquivo é propositalmente grande.
"""

from typing import List, Optional
from uuid import UUID as UUIDType
from datetime import date, timedelta

from sqlalchemy.orm import Session
from sqlalchemy import select


# ✅ CORRETO:
# ✅ CORRETO:
from database.db_models import FollowUp
from schemas.followup import FollowUpCreate, FollowUpUpdate, FollowUpOut


class FollowUpRepository:

    # =========================================================
    # 🔹 CREATE
    # =========================================================
    @staticmethod
    def create(
        db: Session,
        *,
        user_id: int,
        description: str,
        title: Optional[str] = None,
        note_id: Optional[UUIDType] = None,
        due_date: Optional[date] = None,
        priority: str = "MEDIA",
        status: str = "ABERTO",
        source: str = "manual",
    ) -> FollowUp:
        followup = FollowUp(
            user_id=user_id,
            title=title,
            description=description,
            note_id=note_id,
            due_date=due_date,
            priority=priority,
            status=status,
        )

        db.add(followup)
        db.commit()
        db.refresh(followup)

        return followup

    # =========================================================
    # 🔹 GETTERS BÁSICOS (SEGUROS)
    # =========================================================
    @staticmethod
    def get_by_id(
        db: Session,
        *,
        followup_id: int,
        user_id: int,
    ) -> Optional[FollowUp]:
        stmt = select(FollowUp).where(
            FollowUp.id == followup_id,
            FollowUp.user_id == user_id,
        )
        return db.scalars(stmt).first()

    @staticmethod
    def list_by_user(
        db: Session,
        *,
        user_id: int,
        status: Optional[str] = None,
        priority: Optional[str] = None,
        include_closed: bool = False,
    ) -> List[FollowUp]:
        stmt = select(FollowUp).where(FollowUp.user_id == user_id)

        if status:
            stmt = stmt.where(FollowUp.status == status)

        if priority:
            stmt = stmt.where(FollowUp.priority == priority)

        if not include_closed:
            stmt = stmt.where(FollowUp.status != "CONCLUIDO")

        stmt = stmt.order_by(
            FollowUp.due_date.asc().nulls_last(),
            FollowUp.created_at.desc(),
        )

        return list(db.scalars(stmt).all())

    # =========================================================
    # 🔹 DUPLICIDADE / VALIDAÇÃO
    # =========================================================
    @staticmethod
    def find_open_by_note_and_text(
        db: Session,
        *,
        user_id: int,
        note_id: UUIDType,
        description: str,
    ) -> Optional[FollowUp]:
        """
        Busca follow-up ABERTO ligado à mesma note
        com a mesma descrição.
        """
        stmt = select(FollowUp).where(
            FollowUp.user_id == user_id,
            FollowUp.note_id == note_id,
            FollowUp.description == description,
            FollowUp.status != "CONCLUIDO",
        )

        return db.scalars(stmt).first()

    # =========================================================
    # 🔹 AGENDA / PRAZOS
    # =========================================================
    @staticmethod
    def list_due_soon(
        db: Session,
        *,
        user_id: int,
        days_ahead: int = 7,
    ) -> List[FollowUp]:
        """
        Follow-ups com prazo próximo (agenda).
        """
        today = date.today()
        limit_date = today + timedelta(days=days_ahead)

        stmt = select(FollowUp).where(
            FollowUp.user_id == user_id,
            FollowUp.status != "CONCLUIDO",
            FollowUp.due_date.isnot(None),
            FollowUp.due_date <= limit_date,
        )

        stmt = stmt.order_by(FollowUp.due_date.asc())

        return list(db.scalars(stmt).all())

    @staticmethod
    def list_overdue(
        db: Session,
        *,
        user_id: int,
    ) -> List[FollowUp]:
        """
        Follow-ups atrasados.
        """
        today = date.today()

        stmt = select(FollowUp).where(
            FollowUp.user_id == user_id,
            FollowUp.status != "CONCLUIDO",
            FollowUp.due_date.isnot(None),
            FollowUp.due_date < today,
        )

        stmt = stmt.order_by(FollowUp.due_date.asc())

        return list(db.scalars(stmt).all())

    # =========================================================
    # 🔹 STATUS
    # =========================================================
    @staticmethod
    def close(
        db: Session,
        *,
        followup_id: int,
        user_id: int,
    ) -> Optional[FollowUp]:
        stmt = select(FollowUp).where(
            FollowUp.id == followup_id,
            FollowUp.user_id == user_id,
        )

        followup = db.scalars(stmt).first()

        if not followup:
            return None

        followup.status = "CONCLUIDO"
        db.commit()
        db.refresh(followup)

        return followup

    # =========================================================
    # 🔹 MÉTRICAS / KPI (BASE)
    # =========================================================
    @staticmethod
    def count_by_status(
        db: Session,
        *,
        user_id: int,
    ) -> dict:
        """
        Retorna contagem básica por status.
        """
        stmt = select(FollowUp.status).where(
            FollowUp.user_id == user_id
        )

        rows = db.scalars(stmt).all()

        result = {
            "ABERTO": 0,
            "EM-ANDAMENTO": 0,
            "CONCLUIDO": 0,
        }

        for status in rows:
            if status in result:
                result[status] += 1

        return result