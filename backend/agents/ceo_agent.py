#E:\MAWDSLEYS-AGENTE\backend\agents\ceo_agent.py
from openai import OpenAI

from services.ai_service import load_system_prompt
from core.memory.executive_memory_service import ExecutiveMemoryService
from services.json_guard import JSONGuard

client = OpenAI()


class CEOAgent:
    """
    Agente Executivo da CEO (PRODUÇÃO).
    - NÃO é chat
    - NÃO usa embeddings
    - NÃO depende de pergunta
    - SEMPRE retorna estrutura válida
    - Fonte da verdade: captures + memória persistente
    """

    def __init__(self, user_id: str):
        self.user_id = user_id
        self.memory = ExecutiveMemoryService(user_id)

    def process_capture(self, raw_input: str) -> dict:
        # 1️⃣ Carrega prompt executivo fixo
        system_prompt = load_system_prompt()

        # 2️⃣ Monta memória executiva persistente
        memory_context = self.memory.build_context(days=30, limit=20)

        # 3️⃣ Mensagens para a IA
        messages = [
            {
                "role": "system",
                "content": system_prompt
            },
            {
                "role": "system",
                "content": (
                    "HISTÓRICO EXECUTIVO PERSISTENTE (CAPTURES):\n"
                    f"{memory_context}"
                )
            },
            {
                "role": "user",
                "content": raw_input
            }
        ]

        # 4️⃣ Chamada ao modelo
        response = client.chat.completions.create(
            model="gpt-4.1",
            messages=messages,
            temperature=0.1
        )

        # 5️⃣ Blindagem de JSON (NUNCA quebra produção)
        raw_content = response.choices[0].message.content
        structured = JSONGuard.extract_json(raw_content)

        # 6️⃣ Garantias mínimas de contrato (defensivo)
        structured.setdefault("hashtags", ["#DailyLog"])
        structured.setdefault("followups", [])
        structured.setdefault("rituals", [])
        structured.setdefault("directors", [])
        structured.setdefault("actions", [])
        structured.setdefault("register_location", "DailyLog")
        structured.setdefault("confidence_level", "low")

        return structured
