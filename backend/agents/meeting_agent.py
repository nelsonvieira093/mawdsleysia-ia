class MeetingAgent: pass

import os
from openai import OpenAI
from ai_engine.embeddings.embedding_loader import search_relevant

client = OpenAI()

def summarize_meeting(notes: str):
    docs = search_relevant(notes)
    context = "\n".join([d["content"] for d in docs])

    system_prompt = f"""
Você é o MAWDSLEYS — Agente Especialista em Reuniões.

Funções:
- Criar pautas
- Gerar atas de reunião
- Organizar decisões
- Destacar follow-ups
- Linguagem formal e executiva

Contexto relevante:
{context}
"""

    user_prompt = f"Notas da reunião:\n{notes}"

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]
    )

    return response.choices[0].message["content"]
