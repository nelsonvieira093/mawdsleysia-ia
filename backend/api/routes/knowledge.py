from fastapi import APIRouter
from ai_engine.embeddings.embedding_loader import search_relevant

router = APIRouter(prefix="/knowledge", tags=["Knowledge"])

@router.post("/search")
def search(data: dict):
    return search_relevant(data.get("query", ""))
