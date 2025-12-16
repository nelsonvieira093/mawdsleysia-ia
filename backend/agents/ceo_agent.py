class CEOAgent: pass
import os
from openai import OpenAI
from ai_engine.embeddings.embedding_loader import search_relevant

client = OpenAI()

def run_ceo_agent(question: str):
    # Buscando contexto
    docs = search_relevant(question)

    context = "\n\n".join(
        [f"[Documento: {d['title']}]\n{d['content']}" for d in docs]
    )

    system_prompt = f"""
Você é o MAWDSLEYS — Agente Executivo de Diretoria.

Funções principais:
- Responder com precisão executiva
- Fornecer visão estratégica
- Usar o contexto da base de conhecimento quando disponível
- Ser objetivo, direto e confiável

Se houver contexto disponível, utilize para fundamentar a resposta.

Contexto relevante:
{context}
"""

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": question}
        ]
    )

    return response.choices[0].message["content"]
