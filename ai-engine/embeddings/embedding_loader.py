import json
import os
import numpy as np
from  openai import OpenAI

client = OpenAI()

EMBED_PATH = "ai-engine/embeddings/document_embeddings.json"

# --------------------------------------------------
# Carregar embeddings
# --------------------------------------------------
def load_embeddings():
    if not os.path.exists(EMBED_PATH):
        return []
    with open(EMBED_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

# --------------------------------------------------
# Salvar embeddings
# --------------------------------------------------
def save_embeddings(data):
    with open(EMBED_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

# --------------------------------------------------
# Gerar embedding com OpenAI
# --------------------------------------------------
def generate_embedding(text: str):
    response = client.embeddings.create(
        model="text-embedding-3-small",
        input=text
    )
    return response.data[0].embedding

# --------------------------------------------------
# Adicionar um novo documento à base
# --------------------------------------------------
def add_document(doc_id: str, title: str, content: str):
    data = load_embeddings()

    embedding = generate_embedding(content)

    data.append({
        "id": doc_id,
        "title": title,
        "content": content,
        "embedding": embedding
    })

    save_embeddings(data)

    return {"status": "ok", "id": doc_id}

# --------------------------------------------------
# Buscar documentos relevantes
# --------------------------------------------------
def search_relevant(query: str, top_k=3):
    data = load_embeddings()
    if not data:
        return []

    query_emb = np.array(generate_embedding(query))

    scored = []
    for doc in data:
        emb = np.array(doc["embedding"])
        score = float(np.dot(query_emb, emb) / (np.linalg.norm(query_emb) * np.linalg.norm(emb)))
        scored.append((score, doc))

    scored.sort(key=lambda x: x[0], reverse=True)

    return [d for _, d in scored[:top_k]]
