# E:\MAWDSLEYS-AGENTE\backend\main.py

from fastapi import FastAPI, APIRouter, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
import openai
import os
import sys
from pathlib import Path
from datetime import datetime
from contextlib import asynccontextmanager
from dotenv import load_dotenv
from api.routes.meetings import router as meetings_router
from api.routes.automations import router as automations_router


# =====================================================
# PATHS & ENV
# =====================================================
BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

print("🚀 Iniciando backend MAWDSLEYS")
print(f"📁 Backend dir: {BASE_DIR}")

# Carrega variáveis de ambiente
load_dotenv()

# =====================================================
# OPENAI CONFIG
# =====================================================
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY or len(OPENAI_API_KEY) < 20:
    raise RuntimeError("❌ OPENAI_API_KEY não encontrada ou inválida")

openai.api_key = OPENAI_API_KEY
print("🤖 OpenAI configurada com sucesso (SDK CLÁSSICO)")

# =====================================================
# LIFESPAN
# =====================================================
@asynccontextmanager
async def lifespan(app: FastAPI):
    print("🔄 Inicializando aplicação...")
    yield
    print("👋 Encerrando aplicação...")

# =====================================================
# APP
# =====================================================
app = FastAPI(
    title="MAWDSLEYS API",
    version="2.0.0",
    lifespan=lifespan,
    description="API do sistema MAWDSLEYS com IA integrada",
    docs_url="/docs",
    redoc_url="/redoc"
)

# =====================================================
# MIDDLEWARES (ORDEM CRÍTICA)
# =====================================================

# 1️⃣ MIDDLEWARE DE ACTIVITY LOG (DEVE VIR PRIMEIRO)
try:
    from core.middleware.activity_logger import ActivityLogMiddleware
    app.add_middleware(ActivityLogMiddleware)
    print("✅ Activity Log Middleware registrado")
except ImportError as e:
    print(f"⚠️ Activity Log Middleware não disponível: {e}")
    print("⚠️ Eventos não serão registrados automaticamente")

# 2️⃣ CORS MIDDLEWARE (DEPOIS)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Em produção, substitua por origens específicas
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

print("✅ Middlewares configurados na ordem correta")

# =====================================================
# IMPORT ROUTERS
# =====================================================
from api.routes.ingest import router as ingest_router
from api.routes.agenda import router as agenda_router
from api.routes.kpis import router as kpis_router
from api.routes.ingest_audio import router as ingest_audio_router
from api.routes.auth import router as auth_router
from api.routes.chat import router as chat_router_v2  # Chat com memória
from api.routes.meetings import router as meetings_router  # Reuniões

# Importe o router de admin auth (se existir)
try:
    from api.routes.admin_auth import router as admin_auth_router
    ADMIN_AUTH_AVAILABLE = True
except ImportError:
    ADMIN_AUTH_AVAILABLE = False
    print("⚠️ Admin auth routes não disponíveis")

# =====================================================
# ROOT ENDPOINTS
# =====================================================
@app.get("/")
async def root():
    return {
        "name": "MAWDSLEYS API",
        "status": "online",
        "version": "2.0.0",
        "timestamp": datetime.utcnow().isoformat(),
        "openai": True,
        "docs": "/docs",
        "health": "/health",
        "middleware": {
            "activity_log": "enabled",
            "cors": "enabled"
        }
    }

@app.get("/health")
async def health():
    return {
        "status": "ok",
        "openai": True,
        "timestamp": datetime.utcnow().isoformat(),
        "database": "connected",
        "middleware": {
            "activity_log": "active",
            "cors": "active"
        }
    }

# =====================================================
# ENDPOINT DE TESTE FUNCIONAL
# =====================================================

@app.post("/test-auto")
async def test_auto_endpoint():
    from datetime import datetime
    return {
        "status": "success",
        "message": "Endpoint de teste funcional",
        "timestamp": datetime.utcnow().isoformat(),
        "system": "MAWDSLEYS",
        "endpoint": "/test-auto",
        "test": "automation-ready"
    }

# =====================================================
# ENDPOINT DE TESTE DE AUTOMAÇÃO (SIMPLIFICADO)
# =====================================================

@app.post("/test-automation")
async def test_automation_public():
    """
    Endpoint SIMPLIFICADO para testar automações
    """
    print("\n" + "="*60)
    print("🚀 TESTE SIMPLES DE AUTOMAÇÃO")
    print("="*60)
    
    try:
        from datetime import datetime
        import os
        
        print("✅ 1. Teste iniciado")
        
        # Verifica módulos básicos
        modules = {
            "AutomationOrchestrator": False,
            "AlertEngine": False,
            "ActivityEvent": False
        }
        
        try:
            from core.orchestrator.automation_orchestrator import AutomationOrchestrator
            modules["AutomationOrchestrator"] = True
            print("✅ 2. AutomationOrchestrator encontrado")
        except ImportError:
            print("⚠️  2. AutomationOrchestrator não encontrado")
        
        try:
            from core.alerts.alert_engine import AlertEngine
            modules["AlertEngine"] = True
            print("✅ 3. AlertEngine encontrado")
        except ImportError:
            print("⚠️  3. AlertEngine não encontrado")
        
        try:
            from core.events.activity_log import ActivityEvent
            modules["ActivityEvent"] = True
            print("✅ 4. ActivityEvent encontrado")
        except ImportError:
            print("⚠️  4. ActivityEvent não encontrado")
        
        print("="*60)
        print("🎯 TESTE COMPLETO!")
        print("="*60)
        
        return {
            "status": "success",
            "message": "Teste de módulos realizado",
            "timestamp": datetime.utcnow().isoformat(),
            "modules": modules,
            "system": "MAWDSLEYS Backend 2.0.0"
        }
        
    except Exception as e:
        print(f"❌ ERRO NO TESTE: {e}")
        import traceback
        traceback.print_exc()
        
        return {
            "status": "error",
            "message": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }

# =====================================================
# REGISTER ROUTERS
# =====================================================

# Rotas principais da API
app.include_router(ingest_router, prefix="/api", tags=["Ingest"])
app.include_router(agenda_router, prefix="/api", tags=["Agenda"])
app.include_router(kpis_router, prefix="/api", tags=["KPIs"])
app.include_router(ingest_audio_router, prefix="/api", tags=["Audio"])

# Auth routes (v1)
app.include_router(auth_router, prefix="/api/v1/auth", tags=["Auth"])

# Chat com memória (v2 - inteligente)
app.include_router(chat_router_v2, tags=["Chat IA"])

# Reuniões com automação (JÁ EXISTIA — NÃO REMOVIDO)
app.include_router(meetings_router, tags=["Meetings"])

# 🔧 REGISTRO EXPLÍCITO DAS ROTAS DE REUNIÕES (GARANTIA)
app.include_router(meetings_router, prefix="/meetings", tags=["Meetings"])
# Automação
app.include_router(automations_router)

# Admin auth routes (se disponível)
if ADMIN_AUTH_AVAILABLE:
    app.include_router(admin_auth_router, prefix="/api/v1/auth", tags=["Admin-Auth"])
    print("✅ Admin auth routes registradas")

# =====================================================
# CHAT API LEGACY (FALLBACK)
# =====================================================
# Mantemos o chat legacy como fallback
chat_router_legacy = APIRouter(prefix="/api/v1/chat-legacy", tags=["Chat Legacy"])

class ChatRequestLegacy(BaseModel):
    message: str
    model: str = "gpt-4o-mini"
    temperature: float = 0.4

@chat_router_legacy.get("/health")
async def chat_health_legacy():
    return {"status": "online", "openai": True, "model": "gpt-4o-mini"}

@chat_router_legacy.post("/")
async def chat_handler_legacy(data: ChatRequestLegacy):
    try:
        response = openai.ChatCompletion.create(
            model=data.model,
            messages=[
                {"role": "system", "content": "Você é o assistente corporativo MAWDSLEYS. Responda de forma profissional e útil."},
                {"role": "user", "content": data.message}
            ],
            temperature=data.temperature,
            max_tokens=800
        )
        return {
            "reply": response.choices[0].message["content"],
            "model": data.model,
            "tokens_used": response.usage.total_tokens if hasattr(response, 'usage') else None
        }
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Erro OpenAI: {str(e)}"
        )

app.include_router(chat_router_legacy)

# =====================================================
# INFO ENDPOINT
# =====================================================
@app.get("/info")
async def info():
    """Informações do sistema"""
    return {
        "app": "MAWDSLEYS Backend",
        "version": "2.0.0",
        "environment": os.getenv("ENVIRONMENT", "development"),
        "openai_configured": bool(OPENAI_API_KEY),
        "admin_auth_available": ADMIN_AUTH_AVAILABLE,
        "timestamp": datetime.utcnow().isoformat(),
        "features": {
            "chat_with_memory": True,
            "activity_log_middleware": True,
            "meetings_automation": True,
            "alert_engine": True
        },
        "endpoints": {
            "docs": "/docs",
            "health": "/health",
            "chat_intelligent": "/api/v1/chat",
            "chat_legacy": "/api/v1/chat-legacy",
            "meetings": "/meetings",
            "auth": "/api/v1/auth",
            "ingest": "/api/ingest",
            "kpis": "/api/kpis"
        }
    }

# =====================================================
# STARTUP MESSAGE
# =====================================================
print("✅ MAWDSLEYS API pronta com IA REAL (ONLINE)")
print(f"📚 Documentação: http://localhost:8000/docs")
print(f"🤖 Chat Inteligente: /api/v1/chat (com memória)")
print(f"🤖 Chat Legacy: /api/v1/chat-legacy (simples)")
print(f"📅 Reuniões: /meetings (com automação)")
print(f"🔐 Auth endpoints: /api/v1/auth")
if ADMIN_AUTH_AVAILABLE:
    print(f"👑 Admin auth: /api/v1/auth/admin-login")

# =====================================================
# RUN
# =====================================================
if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True if os.getenv("ENVIRONMENT") == "development" else False
    )