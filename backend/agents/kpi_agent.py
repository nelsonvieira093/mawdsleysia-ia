class KPIAgent: pass
import os
from openai import OpenAI
from ai_engine.embeddings.embedding_loader import search_relevant

client = OpenAI()

def analyze_kpi(text: str):
    docs = search_relevant(text)
    context = "\n".join([d["content"] for d in docs])

    system_prompt = f"""
Você é o MAWDSLEYS — Analista de KPIs Corporativos.

Objetivo:
- Interpretar métricas
- Detectar riscos, alertas e tendências
- Sugerir próximos passos
- Falar de forma executiva

Contexto relevante:
{context}
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": text},
        ]
    )

    return response.choices[0].message["content"]
