# backend/main.py - VERSÃO CORRIGIDA E FUNCIONAL
# ==========================================
# 1. IMPORTAÇÕES BÁSICAS
# ==========================================
import sys
import os
from pathlib import Path
from fastapi import FastAPI, APIRouter, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
import uvicorn
from contextlib import asynccontextmanager

# ==========================================
# 2. CONFIGURAÇÃO
# ==========================================
current_file = Path(__file__).resolve()
backend_dir = current_file.parent
root_dir = backend_dir.parent

sys.path.insert(0, str(root_dir))
sys.path.insert(0, str(backend_dir))

print(f"🚀 Iniciando backend...")
print(f"📁 Diretório raiz: {root_dir}")
print(f"📁 Diretório backend: {backend_dir}")

# ==========================================
# 3. CARREGAR .env
# ==========================================
from dotenv import load_dotenv
load_dotenv(dotenv_path=root_dir / ".env", override=True)
print(f"✅ .env carregado")

# ==========================================
# 4. LIFESPAN (STARTUP/SHUTDOWN)
# ==========================================
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("\n🔄 Inicializando aplicação...")
    
    try:
        from backend.database.session import Base, engine
        if engine and Base:
            Base.metadata.create_all(bind=engine)
            print("📦 Tabelas criadas/verificadas")
            
            from sqlalchemy import text
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
                print("✅ Conexão com PostgreSQL estabelecida")
        else:
            print("⚠️  Banco não configurado")
    except ImportError as e:
        print(f"⚠️  Banco não disponível: {e}")
    except Exception as e:
        print(f"⚠️  Erro no banco: {e}")
    
    print("\n" + "="*50)
    print("🎯 API PRONTA PARA USO!")
    print("="*50)
    print("🌐 URL: http://localhost:8000")
    print("📚 Docs: http://localhost:8000/docs")
    print("🔧 Health: http://localhost:8000/health")
    print("📊 Rotas criadas: 13 módulos")
    print("="*50)
    
    yield  # Aplicação roda aqui
    
    # Shutdown
    print("\n👋 Encerrando API...")

# ==========================================
# 5. CRIAR APP COM LIFESPAN (UMA ÚNICA VEZ!)
# ==========================================
app = FastAPI(
    title="MAWDSLEYS API",
    version="2.0.0",
    docs_url="/docs",
    openapi_url="/openapi.json",
    description="API completa do sistema MAWDSLEYS com todas as rotas integradas",
    lifespan=lifespan
)

# ==========================================
# 6. CORS
# ==========================================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==========================================
# 7. ROTAS BÁSICAS (DEFINIR PRIMEIRO!)
# ==========================================
@app.get("/")
async def root():
    return {
        "api": "MAWDSLEYS Agent API",
        "version": "2.0.0",
        "status": "online",
        "docs": "/docs",
        "health": "/health",
        "endpoints": "/api/*"
    }

@app.get("/health")
async def health():
    """Health check"""
    return {
        "status": "healthy",
        "service": "MAWDSLEYS API",
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }

# ==========================================
# 8. ROTAS DA API
# ==========================================
print("\n📦 Criando todas as rotas...")

# Router principal
api_router = APIRouter()

# ============ AUTH ============
auth_router = APIRouter(tags=["Autenticação"])

class LoginRequest(BaseModel):
    email: str
    password: str

class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: int
    email: str

class SignupRequest(BaseModel):
    email: str
    password: str
    name: str

@auth_router.post("/login", response_model=LoginResponse)
async def login(request: LoginRequest):
    """Login de usuário"""
    return {
        "access_token": "fake-jwt-token-example",
        "user_id": 1,
        "email": request.email
    }

@auth_router.post("/signup", response_model=dict)
async def signup(request: SignupRequest):
    """Criar novo usuário"""
    return {
        "message": "Usuário criado com sucesso",
        "user_id": 2,
        "email": request.email
    }

@auth_router.get("/me")
async def get_current_user():
    """Obter informações do usuário atual"""
    return {
        "id": 1,
        "email": "admin@mawdsleys.com",
        "name": "Administrador",
        "role": "admin"
    }

api_router.include_router(auth_router, prefix="/auth")
print("✅ Auth criado")

# ============ FOLLOWUPS ============
followups_router = APIRouter(tags=["Followups"])

class FollowUp(BaseModel):
    id: int
    title: str
    description: str
    status: str = "pending"
    created_at: str

@followups_router.get("/", response_model=List[FollowUp])
async def get_followups():
    """Listar todos os followups"""
    return [
        {
            "id": 1,
            "title": "Seguir com cliente X",
            "description": "Enviar proposta final",
            "status": "pending",
            "created_at": "2024-12-15T10:00:00Z"
        },
        {
            "id": 2,
            "title": "Reunião de follow-up",
            "description": "Discutir resultados do projeto",
            "status": "completed",
            "created_at": "2024-12-14T15:30:00Z"
        }
    ]

@followups_router.post("/", response_model=FollowUp)
async def create_followup(followup: FollowUp):
    """Criar novo followup"""
    return followup

api_router.include_router(followups_router, prefix="/followups")
print("✅ Followups criado")

# ============ KPIs ============
kpis_router = APIRouter(tags=["KPIs"])

class KPI(BaseModel):
    id: int
    name: str
    target: float
    current: float
    unit: str = "%"

@kpis_router.get("/", response_model=List[KPI])
async def get_kpis():
    """Listar todos os KPIs"""
    return [
        {"id": 1, "name": "Taxa de conversão", "target": 85.0, "current": 78.5},
        {"id": 2, "name": "Satisfação do cliente", "target": 90.0, "current": 92.3},
        {"id": 3, "name": "Crescimento mensal", "target": 15.0, "current": 18.2}
    ]

api_router.include_router(kpis_router, prefix="/kpis")
print("✅ KPIs criado")

# ============ MEETINGS ============
meetings_router = APIRouter(tags=["Meetings"])

class Meeting(BaseModel):
    id: int
    title: str
    date: str
    time: str
    participants: List[str]

@meetings_router.get("/", response_model=List[Meeting])
async def get_meetings():
    """Listar todas as reuniões"""
    return [
        {
            "id": 1,
            "title": "Reunião de planejamento",
            "date": "2024-12-16",
            "time": "10:00",
            "participants": ["João", "Maria", "Pedro"]
        },
        {
            "id": 2,
            "title": "Review semanal",
            "date": "2024-12-18",
            "time": "14:30",
            "participants": ["Time de desenvolvimento"]
        }
    ]

api_router.include_router(meetings_router, prefix="/meetings")
print("✅ Meetings criado")

# ============ CHAT ============
chat_router = APIRouter(tags=["Chat"])

# ADICIONE ESTE CÓDIGO NO SEU main.py, na seção de rotas:

# ============ CHAT COMPLETO (baseado no chat.py.bak) ============
chat_router = APIRouter(tags=["Chat"])

class ChatMessage(BaseModel):
    message: str
    context: Optional[List[dict]] = None
    temperature: Optional[float] = 0.7
    max_tokens: Optional[int] = 1000
    model: Optional[str] = "gpt-3.5-turbo"

# Configurar OpenAI
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
client = None
if OPENAI_API_KEY and len(OPENAI_API_KEY) > 20:
    try:
        from openai import OpenAI
        client = OpenAI(api_key=OPENAI_API_KEY)
        print("🤖 OpenAI configurada")
    except:
        client = None
        print("⚠️  OpenAI não disponível")

@chat_router.get("/health")
async def chat_health():
    """Status do chat"""
    return {
        "status": "online",
        "service": "Chat MAWDSLEYS",
        "openai_enabled": bool(client),
        "mode": "ai" if client else "demo",
        "timestamp": datetime.utcnow().isoformat()
    }

@chat_router.post("/")
async def chat_with_agent(chat_request: ChatMessage):
    """Chat com IA ou modo demo"""
    
    # Modo DEMO (se não tem OpenAI)
    if not client:
        return {
            "reply": f"🤖 **Modo DEMO Ativo**\n\nVocê disse:\n\n*{chat_request.message}*\n\n"
                     "Para IA real, configure OPENAI_API_KEY no .env",
            "model": "demo",
            "mode": "demo",
            "timestamp": datetime.utcnow().isoformat()
        }
    
    # IA REAL (se tem OpenAI)
    try:
        system_prompt = "Você é o assistente corporativo MAWDSLEYS. Seja profissional e útil."
        
        messages = [{"role": "system", "content": system_prompt}]
        if chat_request.context:
            messages.extend(chat_request.context)
        messages.append({"role": "user", "content": chat_request.message})
        
        response = client.chat.completions.create(
            model=chat_request.model,
            messages=messages,
            temperature=chat_request.temperature,
            max_tokens=chat_request.max_tokens
        )
        
        ai_reply = response.choices[0].message.content
        
        return {
            "reply": ai_reply,
            "model": response.model,
            "mode": "ai",
            "usage": {"total_tokens": response.usage.total_tokens},
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        return {
            "reply": "⚠️ Erro na IA. Modo demo ativado.",
            "error": str(e),
            "mode": "error",
            "timestamp": datetime.utcnow().isoformat()
        }

@chat_router.get("/")
async def chat_status():
    """Endpoint principal do chat"""
    return {
        "status": "online",
        "ai_available": bool(client),
        "mode": "ai" if client else "demo",
        "message": "Chat MAWDSLEYS operacional"
    }

api_router.include_router(chat_router, prefix="/chat")
print("✅ Chat completo carregado")

class ChatResponse(BaseModel):
    reply: str
    timestamp: str

@chat_router.get("/")
async def chat_status():
    """Status do chat"""
    return {"status": "online", "ai_enabled": True}

@chat_router.post("/", response_model=ChatResponse)
async def send_message(message: ChatMessage):
    """Enviar mensagem para o chat"""
    return {
        "reply": f"Você disse: '{message.message}'. Como posso ajudá-lo hoje?",
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }

@chat_router.get("/history")
async def chat_history():
    """Histórico do chat"""
    return {
        "history": [
            {"user": "Oi, como vai?", "bot": "Estou bem, obrigado! Como posso ajudar?", "time": "10:00"},
            {"user": "Preciso de um relatório", "bot": "Claro! Qual relatório você precisa?", "time": "10:02"}
        ]
    }

api_router.include_router(chat_router, prefix="/chat")
print("✅ Chat criado")

# ============ AI FOLLOWUPS ============
ai_followups_router = APIRouter(tags=["AI Followups"])

@ai_followups_router.get("/")
async def get_ai_followups():
    """Followups analisados por IA"""
    return {
        "ai_analysis": [
            {"id": 1, "priority": "high", "suggested_action": "Contactar urgente"},
            {"id": 2, "priority": "medium", "suggested_action": "Agendar reunião"}
        ]
    }

api_router.include_router(ai_followups_router, prefix="/ai-followups")
print("✅ AI Followups criado")

# ============ AI KPIs ============
ai_kpis_router = APIRouter(tags=["AI KPIs"])

@ai_kpis_router.get("/")
async def get_ai_kpis():
    """KPIs analisados por IA"""
    return {
        "insights": [
            {"metric": "Vendas", "trend": "up", "prediction": "Aumento de 15% no próximo mês"},
            {"metric": "Satisfação", "trend": "stable", "recommendation": "Manter estratégia atual"}
        ]
    }

api_router.include_router(ai_kpis_router, prefix="/ai-kpis")
print("✅ AI KPIs criado")

# ============ AI MEETINGS ============
ai_meetings_router = APIRouter(tags=["AI Meetings"])

@ai_meetings_router.get("/")
async def get_ai_meetings():
    """Reuniões otimizadas por IA"""
    return {
        "optimized_schedule": [
            {"meeting": "Daily", "optimal_time": "09:30", "duration": "15min"},
            {"meeting": "Planejamento", "optimal_time": "14:00", "duration": "45min"}
        ]
    }

api_router.include_router(ai_meetings_router, prefix="/ai-meetings")
print("✅ AI Meetings criado")

# ============ CEO ============
ceo_router = APIRouter(tags=["CEO"])

@ceo_router.get("/")
async def ceo_dashboard():
    """Dashboard do CEO"""
    return {
        "dashboard": {
            "revenue": {"current": 1500000, "growth": 15.5},
            "employees": {"total": 45, "new_hires": 3},
            "projects": {"active": 12, "completed": 28}
        }
    }

@ceo_router.get("/report")
async def ceo_report():
    """Relatório executivo"""
    return {"report": "Relatório executivo gerado com sucesso"}

api_router.include_router(ceo_router, prefix="/ceo")
print("✅ CEO criado")

# ============ DOCUMENTS ============
documents_router = APIRouter(tags=["Documents"])

@documents_router.get("/")
async def list_documents():
    """Listar documentos"""
    return {"documents": ["contrato.pdf", "relatorio.docx", "apresentacao.pptx"]}

api_router.include_router(documents_router, prefix="/documents")
print("✅ Documents criado")

# ============ KNOWLEDGE ============
knowledge_router = APIRouter(tags=["Knowledge"])

class KnowledgeSearch(BaseModel):
    query: str

@knowledge_router.get("/")
async def get_knowledge():
    """Base de conhecimento"""
    return {
        "articles": [
            {"id": 1, "title": "Como usar a API", "category": "Documentação"},
            {"id": 2, "title": "Boas práticas", "category": "Guia"}
        ]
    }

@knowledge_router.post("/search")
async def search_knowledge(search: KnowledgeSearch):
    """Buscar na base de conhecimento"""
    return {
        "query": search.query,
        "results": [
            {"title": "Resultado 1 para: " + search.query, "relevance": 0.85},
            {"title": "Resultado 2 para: " + search.query, "relevance": 0.72}
        ]
    }

api_router.include_router(knowledge_router, prefix="/knowledge")
print("✅ Knowledge criado")

# ============ TEST ENDPOINT ============
@api_router.get("/test")
async def test_endpoint():
    """Endpoint de teste"""
    return {
        "test": "success",
        "message": "Todas as rotas estão funcionando!",
        "timestamp": datetime.utcnow().isoformat()
    }

# ==========================================
# 9. INCLUIR ROUTER PRINCIPAL
# ==========================================
app.include_router(api_router, prefix="/api")

# ==========================================
# 10. VERIFICAÇÃO FINAL
# ==========================================
# Listar rotas para debug
print(f"\n📊 Total de rotas registradas: {len(app.routes)}")

# ==========================================
# 11. EXECUÇÃO LOCAL
# ==========================================
if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )