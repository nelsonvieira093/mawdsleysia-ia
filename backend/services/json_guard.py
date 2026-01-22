import json
import re
from typing import Dict


class JSONGuard:
    """
    Blindagem de respostas da IA.
    Garante retorno estruturado mesmo em falhas.
    """

    @staticmethod
    def extract_json(text: str) -> Dict:
        """
        Tenta extrair JSON válido de uma resposta textual.
        """
        try:
            return json.loads(text)
        except Exception:
            pass

        # Tentativa 2 — extrair bloco JSON do texto
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if match:
            try:
                return json.loads(match.group())
            except Exception:
                pass

        # Fallback final — encapsular resposta
        return {
            "hashtags": ["#DailyLog"],
            "summary": "Resposta não estruturada corretamente pela IA.",
            "followups": [],
            "rituals": ["Daily"],
            "directors": [],
            "actions": [],
            "register_location": "DailyLog",
            "confidence_level": "low",
            "_raw_ai_output": text
        }
