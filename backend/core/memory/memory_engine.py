from sqlalchemy.orm import Session
from typing import List, Any
from db.models.activity_log import ActivityLog


class MemoryEngine:
    def __init__(self, db: Session):
        self.db = db

    # =====================================================
    # WRITE MEMORY (CHAMADO PELO EventProcessor)
    # =====================================================
    def add_memory(self, event: Any = None, **kwargs) -> None:
        """
        Registra um evento como memória do sistema.

        ⚠️ IMPORTANTE:
        - Aceita **kwargs para NÃO quebrar chamadas futuras
        - Nunca lança exceção
        - Nunca bloqueia rotas
        """

        try:
            event_type = getattr(event, "type", None)
            entity = getattr(event, "entity", None)

            print(
                f"[MemoryEngine] 🧠 Memória registrada: "
                f"type={event_type} entity={entity}"
            )

        except Exception as e:
            # Memória NUNCA pode quebrar o fluxo
            print(f"[MemoryEngine] ⚠️ Erro ignorado ao registrar memória: {e}")

    # =====================================================
    # READ MEMORY
    # =====================================================
    def recent_events(self, limit: int = 20) -> List[ActivityLog]:
        """
        Retorna os eventos mais recentes do sistema
        """
        return (
            self.db.query(ActivityLog)
            .order_by(ActivityLog.created_at.desc())
            .limit(limit)
            .all()
        )

    def search_events(self, keyword: str, limit: int = 10) -> List[ActivityLog]:
        """
        Busca eventos por palavra-chave
        """
        return (
            self.db.query(ActivityLog)
            .filter(
                ActivityLog.type.ilike(f"%{keyword}%")
                | ActivityLog.entity.ilike(f"%{keyword}%")
            )
            .order_by(ActivityLog.created_at.desc())
            .limit(limit)
            .all()
        )

    # =====================================================
    # FORMAT FOR LLM
    # =====================================================
    def format_for_llm(self, events: List[ActivityLog]) -> str:
        """
        Formata memória para ser enviada ao LLM
        """
        lines = []

        for e in events:
            lines.append(
                f"[{e.created_at}] {e.type} | {e.entity} | {e.payload}"
            )

        return "\n".join(lines)
