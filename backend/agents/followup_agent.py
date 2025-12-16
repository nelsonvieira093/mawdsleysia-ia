class FollowUpAgent: pass
import os
from openai import OpenAI
from ai_engine.embeddings.embedding_loader import search_relevant

client = OpenAI()

def generate_followup(task: str, responsible: str):
    docs = search_relevant(task)
    context = "\n".join([d["content"] for d in docs])

    system_prompt = f"""
Você é o MAWDSLEYS — Agente Especialista em Follow-Ups.

Sua missão:
- Criar follow-ups profissionais
- Linguagem executiva
- Objetivo e direto
- Pressão sem ser agressivo
- Incluir datas quando possível

Contexto relacionado:
{context}
"""

    user_prompt = f"""
Crie um follow-up para:

Tarefa: {task}
Responsável: {responsible}
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]
    )

    return response.choices[0].message["content"]
