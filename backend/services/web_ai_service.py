# E:\MAWDSLEYS-AGENTE\backend\services\web_ai_service.py
import os
import openai  # ✅ CORRIGIDO
from services.ai_service import load_system_prompt
from pathlib import Path


WEB_PROMPT_PATH = (
    Path(__file__).resolve()
    .parent.parent.parent
    / "ai-engine"
    / "prompts"
    / "web_chat_prompt.txt"
)


def load_web_prompt() -> str:
    return WEB_PROMPT_PATH.read_text(encoding="utf-8")


def run_web_chat(question: str) -> str:
    messages = [
        {"role": "system", "content": load_web_prompt()},
        {"role": "user", "content": question}
    ]

    response = openai.ChatCompletion.create(  # ✅ CORRIGIDO
        model="gpt-4.1",
        messages=messages,
        temperature=0.3
    )

    return response.choices[0].message.content