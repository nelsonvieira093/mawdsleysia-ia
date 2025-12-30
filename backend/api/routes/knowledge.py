# backend/api/routes/knowledge.py
from fastapi import APIRouter, Depends, HTTPException, status, Query, Body
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field
import uuid

from database.session import get_db
from api.routes.auth import require_any_auth
# Tenta importar o motor de embeddings; se não disponível, define um fallback leve
try:
    from ai_engine.embeddings.embedding_loader import search_relevant
except Exception:
    def search_relevant(query, limit=10, **kwargs):
        """
        Fallback simples para search_relevant: utiliza o serviço mock local se disponível
        ou retorna lista vazia para evitar erro de importação.
        """
        try:
            # KnowledgeService é definido abaixo neste arquivo; resolução ocorre em tempo de execução.
            return KnowledgeService.search_knowledge(query=query, limit=limit)
        except NameError:
            return []

router = APIRouter(prefix="/knowledge", tags=["Knowledge"])

# ==========================
# SCHEMAS
# ==========================
class KnowledgeBaseCreate(BaseModel):
    """Schema para criar uma base de conhecimento"""
    name: str = Field(..., min_length=1, max_length=200, example="Manual do Produto X")
    description: str = Field(..., max_length=1000, example="Documentação completa do produto X")
    category: str = Field(..., max_length=100, example="Produtos")
    tags: List[str] = Field(default_factory=list, example=["produto", "manual", "documentação"])
    is_public: bool = Field(False, description="Se a base de conhecimento é pública")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)

class KnowledgeItemCreate(BaseModel):
    """Schema para criar um item de conhecimento"""
    title: str = Field(..., min_length=1, max_length=500, example="Como instalar o produto")
    content: str = Field(..., min_length=10, example="Passo 1: Desembale o produto...")
    content_type: str = Field("text", pattern="^(text|markdown|html|code)$")
    category: Optional[str] = Field(None, max_length=100)
    tags: List[str] = Field(default_factory=list, example=["instalação", "guia"])
    source: Optional[str] = Field(None, max_length=200, example="Manual do Fabricante")
    source_url: Optional[str] = Field(None, max_length=500)
    language: str = Field("pt-BR", max_length=10)
    priority: int = Field(1, ge=1, le=5, description="Prioridade de 1 a 5")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)

class SearchQuery(BaseModel):
    """Schema para busca"""
    query: str = Field(..., min_length=1, example="Como fazer instalação?")
    limit: int = Field(10, ge=1, le=100)
    threshold: float = Field(0.7, ge=0.0, le=1.0)
    categories: Optional[List[str]] = None
    tags: Optional[List[str]] = None
    language: Optional[str] = "pt-BR"

class ChatQuery(BaseModel):
    """Schema para chat com conhecimento"""
    question: str = Field(..., min_length=1, example="Como resolver erro X?")
    context: Optional[str] = Field(None, description="Contexto adicional")
    conversation_id: Optional[str] = Field(None, description="ID da conversa para histórico")
    max_results: int = Field(5, ge=1, le=20)

class KnowledgeBaseResponse(BaseModel):
    """Schema de resposta para base de conhecimento"""
    id: str
    name: str
    description: str
    category: str
    tags: List[str]
    is_public: bool
    item_count: int
    created_at: datetime
    updated_at: datetime
    created_by: Optional[int]
    
    class Config:
        from_attributes = True

class KnowledgeItemResponse(BaseModel):
    """Schema de resposta para item de conhecimento"""
    id: str
    title: str
    content: str
    content_type: str
    category: Optional[str]
    tags: List[str]
    source: Optional[str]
    source_url: Optional[str]
    language: str
    priority: int
    relevance_score: Optional[float] = None
    knowledge_base_id: str
    created_at: datetime
    updated_at: datetime
    created_by: Optional[int]
    
    class Config:
        from_attributes = True

class SearchResponse(BaseModel):
    """Schema de resposta para busca"""
    query: str
    results: List[KnowledgeItemResponse]
    total_results: int
    search_time: float
    suggested_queries: List[str] = Field(default_factory=list)

class ChatResponse(BaseModel):
    """Schema de resposta para chat"""
    question: str
    answer: str
    sources: List[KnowledgeItemResponse] = Field(default_factory=list)
    confidence: float
    conversation_id: str
    search_time: float

# ==========================
# MOCK DATA & SERVICES (para desenvolvimento)
# ==========================
class KnowledgeService:
    """Serviço mock para desenvolvimento"""
    
    _knowledge_bases = [
        {
            "id": "kb_001",
            "name": "Manual do Produto X",
            "description": "Documentação completa do produto X",
            "category": "Produtos",
            "tags": ["produto", "manual", "documentação"],
            "is_public": True,
            "item_count": 15,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "created_by": 1
        },
        {
            "id": "kb_002", 
            "name": "FAQ Suporte",
            "description": "Perguntas frequentes de suporte",
            "category": "Suporte",
            "tags": ["faq", "suporte", "ajuda"],
            "is_public": True,
            "item_count": 42,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "created_by": 2
        }
    ]
    
    _knowledge_items = [
        {
            "id": "ki_001",
            "title": "Como instalar o produto X",
            "content": "Passo 1: Desembale o produto. Passo 2: Conecte na energia. Passo 3: Siga o assistente de configuração.",
            "content_type": "text",
            "category": "Instalação",
            "tags": ["instalação", "setup", "início"],
            "source": "Manual do Fabricante",
            "source_url": "https://exemplo.com/manual",
            "language": "pt-BR",
            "priority": 1,
            "knowledge_base_id": "kb_001",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "created_by": 1
        },
        {
            "id": "ki_002",
            "title": "Solução para erro 'Dispositivo não encontrado'",
            "content": "1. Verifique a conexão USB. 2. Reinicie o computador. 3. Atualize os drivers.",
            "content_type": "text",
            "category": "Troubleshooting",
            "tags": ["erro", "suporte", "solução"],
            "source": "Base de Conhecimento Interna",
            "language": "pt-BR",
            "priority": 2,
            "knowledge_base_id": "kb_002",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "created_by": 2
        },
        {
            "id": "ki_003",
            "title": "Configuração de rede avançada",
            "content": "Para configurar rede avançada, acesse Configurações > Rede > Avançado.",
            "content_type": "text",
            "category": "Configuração",
            "tags": ["rede", "configuração", "avançado"],
            "language": "pt-BR",
            "priority": 3,
            "knowledge_base_id": "kb_001",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "created_by": 1
        }
    ]
    
    @classmethod
    def search_knowledge(cls, query: str, limit: int = 10, **filters) -> List[Dict]:
        """Busca em conhecimento (mock)"""
        results = []
        
        for item in cls._knowledge_items:
            # Simulação de busca simples
            score = 0.0
            query_lower = query.lower()
            
            # Verifica no título
            if query_lower in item["title"].lower():
                score += 0.7
            
            # Verifica no conteúdo
            if query_lower in item["content"].lower():
                score += 0.3
            
            # Verifica nas tags
            for tag in item["tags"]:
                if query_lower in tag.lower():
                    score += 0.2
            
            # Aplica filtros
            if filters.get("category") and item["category"] not in filters["category"]:
                continue
            
            if filters.get("tags"):
                if not any(tag in item["tags"] for tag in filters["tags"]):
                    continue
            
            if filters.get("language") and item["language"] != filters["language"]:
                continue
            
            if score > 0:
                item_with_score = item.copy()
                item_with_score["relevance_score"] = min(score, 1.0)
                results.append(item_with_score)
        
        # Ordena por score
        results.sort(key=lambda x: x["relevance_score"], reverse=True)
        return results[:limit]
    
    @classmethod
    def chat_with_knowledge(cls, question: str, max_results: int = 5) -> Dict:
        """Chat com base de conhecimento (mock)"""
        results = cls.search_knowledge(question, limit=max_results)
        
        # Gera resposta baseada nos resultados
        if results:
            answer = f"Baseado na nossa base de conhecimento sobre '{question}':\n\n"
            for i, result in enumerate(results[:3], 1):
                answer += f"{i}. {result['title']}: {result['content'][:100]}...\n"
            answer += "\nPara mais detalhes, consulte os itens completos."
            confidence = 0.8
        else:
            answer = "Desculpe, não encontrei informações específicas sobre isso na base de conhecimento. Posso ajudar com outras questões?"
            confidence = 0.2
        
        return {
            "answer": answer,
            "sources": results,
            "confidence": confidence
        }
    
    @classmethod
    def get_knowledge_base(cls, kb_id: str) -> Optional[Dict]:
        """Obtém uma base de conhecimento"""
        for kb in cls._knowledge_bases:
            if kb["id"] == kb_id:
                return kb
        return None
    
    @classmethod
    def get_knowledge_item(cls, item_id: str) -> Optional[Dict]:
        """Obtém um item de conhecimento"""
        for item in cls._knowledge_items:
            if item["id"] == item_id:
                return item
        return None

# ==========================
# ROTAS DE CONHECIMENTO
# ==========================
@router.post("/search", response_model=SearchResponse)
def search_knowledge(
    search_query: SearchQuery,
    current_user: dict = Depends(require_any_auth)
):
    """Buscar na base de conhecimento"""
    try:
        # Primeiro tenta usar o motor de embeddings real
        if hasattr(search_relevant, '__call__'):
            # Se a função existe, tenta usá-la
            ai_results = search_relevant(search_query.query)
            # Converte resultados para o formato esperado
            results = []
            for result in ai_results[:search_query.limit]:
                results.append({
                    "id": str(uuid.uuid4()),
                    "title": result.get("title", "Resultado da busca"),
                    "content": result.get("content", result.get("text", "")),
                    "content_type": "text",
                    "category": "Busca AI",
                    "tags": ["ai_search"],
                    "language": search_query.language,
                    "priority": 1,
                    "relevance_score": result.get("score", 0.8),
                    "knowledge_base_id": "ai_search",
                    "created_at": datetime.utcnow(),
                    "updated_at": datetime.utcnow(),
                    "created_by": current_user.get("user_id")
                })
        else:
            # Fallback para mock
            results = KnowledgeService.search_knowledge(
                query=search_query.query,
                limit=search_query.limit,
                category=search_query.categories,
                tags=search_query.tags,
                language=search_query.language
            )
        
        # Gera sugestões de busca
        suggested_queries = [
            f"{search_query.query} avançado",
            f"tutorial {search_query.query}",
            f"como fazer {search_query.query}"
        ]
        
        return SearchResponse(
            query=search_query.query,
            results=results,
            total_results=len(results),
            search_time=0.5,  # Mock
            suggested_queries=suggested_queries[:3]
        )
        
    except Exception as e:
        # Fallback completo para mock em caso de erro
        results = KnowledgeService.search_knowledge(
            query=search_query.query,
            limit=search_query.limit
        )
        
        return SearchResponse(
            query=search_query.query,
            results=results,
            total_results=len(results),
            search_time=0.3
        )

@router.post("/chat", response_model=ChatResponse)
def chat_with_knowledge(
    chat_query: ChatQuery,
    current_user: dict = Depends(require_any_auth)
):
    """Conversar com a base de conhecimento (Q&A)"""
    conversation_id = chat_query.conversation_id or str(uuid.uuid4())
    
    response = KnowledgeService.chat_with_knowledge(
        question=chat_query.question,
        max_results=chat_query.max_results
    )
    
    return ChatResponse(
        question=chat_query.question,
        answer=response["answer"],
        sources=response["sources"],
        confidence=response["confidence"],
        conversation_id=conversation_id,
        search_time=0.7
    )

@router.get("/bases", response_model=List[KnowledgeBaseResponse])
def list_knowledge_bases(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=200),
    category: Optional[str] = None,
    is_public: Optional[bool] = None,
    current_user: dict = Depends(require_any_auth)
):
    """Listar bases de conhecimento"""
    bases = KnowledgeService._knowledge_bases
    
    # Aplica filtros
    if category:
        bases = [b for b in bases if b["category"] == category]
    
    if is_public is not None:
        bases = [b for b in bases if b["is_public"] == is_public]
    
    return bases[skip:skip + limit]

@router.get("/bases/{kb_id}", response_model=KnowledgeBaseResponse)
def get_knowledge_base(
    kb_id: str,
    current_user: dict = Depends(require_any_auth)
):
    """Obter detalhes de uma base de conhecimento"""
    kb = KnowledgeService.get_knowledge_base(kb_id)
    if not kb:
        raise HTTPException(status_code=404, detail="Base de conhecimento não encontrada")
    
    # Verifica se o usuário tem acesso
    if not kb["is_public"] and kb["created_by"] != current_user.get("user_id"):
        raise HTTPException(status_code=403, detail="Acesso não autorizado")
    
    return kb

@router.get("/items", response_model=List[KnowledgeItemResponse])
def list_knowledge_items(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=200),
    kb_id: Optional[str] = None,
    category: Optional[str] = None,
    tag: Optional[str] = None,
    current_user: dict = Depends(require_any_auth)
):
    """Listar itens de conhecimento"""
    items = KnowledgeService._knowledge_items
    
    # Aplica filtros
    if kb_id:
        items = [i for i in items if i["knowledge_base_id"] == kb_id]
    
    if category:
        items = [i for i in items if i["category"] == category]
    
    if tag:
        items = [i for i in items if tag in i["tags"]]
    
    return items[skip:skip + limit]

@router.get("/items/{item_id}", response_model=KnowledgeItemResponse)
def get_knowledge_item(
    item_id: str,
    current_user: dict = Depends(require_any_auth)
):
    """Obter detalhes de um item de conhecimento"""
    item = KnowledgeService.get_knowledge_item(item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item de conhecimento não encontrado")
    
    return item

@router.post("/bases", response_model=KnowledgeBaseResponse, status_code=status.HTTP_201_CREATED)
def create_knowledge_base(
    kb_data: KnowledgeBaseCreate,
    current_user: dict = Depends(require_any_auth)
):
    """Criar nova base de conhecimento"""
    user_id = current_user.get("user_id")
    if not user_id:
        raise HTTPException(status_code=401, detail="Usuário não autenticado")
    
    new_kb = {
        "id": f"kb_{uuid.uuid4().hex[:8]}",
        "name": kb_data.name,
        "description": kb_data.description,
        "category": kb_data.category,
        "tags": kb_data.tags,
        "is_public": kb_data.is_public,
        "item_count": 0,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
        "created_by": user_id,
        "metadata": kb_data.metadata
    }
    
    KnowledgeService._knowledge_bases.append(new_kb)
    return new_kb

@router.post("/items", response_model=KnowledgeItemResponse, status_code=status.HTTP_201_CREATED)
def create_knowledge_item(
    item_data: KnowledgeItemCreate,
    kb_id: str = Query(..., description="ID da base de conhecimento"),
    current_user: dict = Depends(require_any_auth)
):
    """Criar novo item de conhecimento"""
    user_id = current_user.get("user_id")
    if not user_id:
        raise HTTPException(status_code=401, detail="Usuário não autenticado")
    
    # Verifica se a base existe
    kb = KnowledgeService.get_knowledge_base(kb_id)
    if not kb:
        raise HTTPException(status_code=404, detail="Base de conhecimento não encontrada")
    
    # Verifica permissão
    if not kb["is_public"] and kb["created_by"] != user_id:
        raise HTTPException(status_code=403, detail="Sem permissão para adicionar itens")
    
    new_item = {
        "id": f"ki_{uuid.uuid4().hex[:8]}",
        "title": item_data.title,
        "content": item_data.content,
        "content_type": item_data.content_type,
        "category": item_data.category,
        "tags": item_data.tags,
        "source": item_data.source,
        "source_url": item_data.source_url,
        "language": item_data.language,
        "priority": item_data.priority,
        "knowledge_base_id": kb_id,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
        "created_by": user_id,
        "metadata": item_data.metadata
    }
    
    KnowledgeService._knowledge_items.append(new_item)
    
    # Atualiza contagem na base
    kb["item_count"] = len([i for i in KnowledgeService._knowledge_items 
                           if i["knowledge_base_id"] == kb_id])
    kb["updated_at"] = datetime.utcnow()
    
    return new_item

@router.get("/suggest")
def suggest_queries(
    q: str = Query(..., min_length=1),
    limit: int = Query(5, ge=1, le=10)
):
    """Sugerir consultas de busca"""
    suggestions = [
        f"{q} passo a passo",
        f"tutorial completo {q}",
        f"como resolver problemas com {q}",
        f"melhores práticas {q}",
        f"{q} configuração avançada",
        f"{q} para iniciantes",
        f"guia rápido {q}",
        f"{q} FAQ"
    ]
    
    return {
        "query": q,
        "suggestions": suggestions[:limit]
    }

@router.get("/stats")
def get_knowledge_stats(
    current_user: dict = Depends(require_any_auth)
):
    """Obter estatísticas da base de conhecimento"""
    total_bases = len(KnowledgeService._knowledge_bases)
    total_items = len(KnowledgeService._knowledge_items)
    
    # Contagem por categoria
    categories = {}
    for item in KnowledgeService._knowledge_items:
        cat = item["category"] or "Sem categoria"
        categories[cat] = categories.get(cat, 0) + 1
    
    # Top tags
    tags_count = {}
    for item in KnowledgeService._knowledge_items:
        for tag in item["tags"]:
            tags_count[tag] = tags_count.get(tag, 0) + 1
    
    top_tags = sorted(tags_count.items(), key=lambda x: x[1], reverse=True)[:10]
    
    return {
        "total_bases": total_bases,
        "total_items": total_items,
        "public_bases": len([b for b in KnowledgeService._knowledge_bases if b["is_public"]]),
        "items_by_category": categories,
        "top_tags": dict(top_tags),
        "last_updated": datetime.utcnow().isoformat()
    }

@router.post("/batch/upload")
def batch_upload(
    items: List[KnowledgeItemCreate],
    kb_id: str = Body(...),
    current_user: dict = Depends(require_any_auth)
):
    """Upload em lote de itens de conhecimento"""
    user_id = current_user.get("user_id")
    if not user_id:
        raise HTTPException(status_code=401, detail="Usuário não autenticado")
    
    # Verifica se a base existe
    kb = KnowledgeService.get_knowledge_base(kb_id)
    if not kb:
        raise HTTPException(status_code=404, detail="Base de conhecimento não encontrada")
    
    created_items = []
    for item_data in items:
        new_item = {
            "id": f"ki_{uuid.uuid4().hex[:8]}",
            "title": item_data.title,
            "content": item_data.content,
            "content_type": item_data.content_type,
            "category": item_data.category,
            "tags": item_data.tags,
            "source": item_data.source,
            "source_url": item_data.source_url,
            "language": item_data.language,
            "priority": item_data.priority,
            "knowledge_base_id": kb_id,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "created_by": user_id,
            "metadata": item_data.metadata
        }
        
        KnowledgeService._knowledge_items.append(new_item)
        created_items.append(new_item)
    
    # Atualiza contagem
    kb["item_count"] = len([i for i in KnowledgeService._knowledge_items 
                           if i["knowledge_base_id"] == kb_id])
    kb["updated_at"] = datetime.utcnow()
    
    return {
        "message": f"{len(created_items)} itens criados com sucesso",
        "items_created": len(created_items),
        "kb_id": kb_id,
        "kb_new_count": kb["item_count"]
    }

@router.get("/health")
def knowledge_health():
    """Health check do módulo de conhecimento"""
    return {
        "status": "healthy",
        "service": "knowledge",
        "timestamp": datetime.utcnow().isoformat(),
        "stats": {
            "bases_count": len(KnowledgeService._knowledge_bases),
            "items_count": len(KnowledgeService._knowledge_items),
            "ai_search_available": hasattr(search_relevant, '__call__')
        }
    }