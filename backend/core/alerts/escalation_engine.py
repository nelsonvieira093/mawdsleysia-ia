# E:\MAWDSLEYS-AGENTE\backend\core\alerts\escalation_engine.py

class EscalationEngine:
    def should_escalate(self, attempts: int) -> bool:
        # Primeira versão simples
        return attempts >= 1
