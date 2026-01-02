#E:\MAWDSLEYS-AGENTE\backend\main.py
import os
import sys
from pathlib import Path
from datetime import datetime
from contextlib import asynccontextmanager
from dotenv import load_dotenv

from fastapi import FastAPI, APIRouter, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
import openai

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
# CORS
# =====================================================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Em produção, substitua por origens específicas
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =====================================================
# IMPORT ROUTERS
# =====================================================
from api.routes.ingest import router as ingest_router
from api.routes.agenda import router as agenda_router
from api.routes.kpis import router as kpis_router
from api.routes.ingest_audio import router as ingest_audio_router
from api.routes.auth import router as auth_router

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
        "health": "/health"
    }

@app.get("/health")
async def health():
    return {
        "status": "ok",
        "openai": True,
        "timestamp": datetime.utcnow().isoformat(),
        "database": "connected"  # Adicione verificação real se tiver banco
    }

# =====================================================
# REGISTER ROUTERS
# =====================================================
# API v1 routes
app.include_router(ingest_router, prefix="/api", tags=["Ingest"])
app.include_router(agenda_router, prefix="/api", tags=["Agenda"])
app.include_router(kpis_router, prefix="/api", tags=["KPIs"])
app.include_router(ingest_audio_router, prefix="/api", tags=["Audio"])

# Auth routes (v1)
app.include_router(auth_router, prefix="/api/v1/auth", tags=["Auth"])

# Admin auth routes (se disponível)
if ADMIN_AUTH_AVAILABLE:
    app.include_router(admin_auth_router, prefix="/api/v1/auth", tags=["Admin-Auth"])
    print("✅ Admin auth routes registradas")

# =====================================================
# CHAT API
# =====================================================
chat_router = APIRouter(prefix="/api/v1/chat", tags=["Chat"])

class ChatRequest(BaseModel):
    message: str
    model: str = "gpt-4o-mini"
    temperature: float = 0.4

@chat_router.get("/health")
async def chat_health():
    return {"status": "online", "openai": True, "model": "gpt-4o-mini"}

@chat_router.post("/")
async def chat_handler(data: ChatRequest):
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

app.include_router(chat_router)

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
        "endpoints": {
            "docs": "/docs",
            "health": "/health",
            "chat": "/api/v1/chat",
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
