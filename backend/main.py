import os
import sys
from pathlib import Path
from datetime import datetime
from contextlib import asynccontextmanager

from fastapi import FastAPI, APIRouter, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
import openai
from api.routes.kpis import router as kpis_router
from api.routes.ingest_audio import router as ingest_audio_router






# =====================================================
# PATHS
# =====================================================
BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

print("🚀 Iniciando backend MAWDSLEYS")
print(f"📁 Backend dir: {BASE_DIR}")

# =====================================================
# ENV
# =====================================================
from dotenv import load_dotenv
load_dotenv()

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
# APP (ÚNICO)
# =====================================================
app = FastAPI(
    title="MAWDSLEYS API",
    version="2.0.0",
    lifespan=lifespan
)

# =====================================================
# CORS
# =====================================================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# =====================================================
# ROOT
# =====================================================
@app.get("/")
async def root():
    return {
        "name": "MAWDSLEYS API",
        "status": "online",
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/health")
async def health():
    return {
        "status": "ok",
        "openai": True,
        "timestamp": datetime.utcnow().isoformat()
    }

# =====================================================
# ROUTERS
# =====================================================
from api.routes.ingest import router as ingest_router
from api.routes.agenda import router as agenda_router

app.include_router(ingest_router, prefix="/api")
app.include_router(agenda_router)
app.include_router(kpis_router, prefix="/api") 
app.include_router(ingest_audio_router, prefix="/api")

# =====================================================
# CHAT
# =====================================================
api = APIRouter(prefix="/api")
chat = APIRouter(prefix="/chat", tags=["Chat"])

class ChatRequest(BaseModel):
    message: str

@chat.get("/health")
async def chat_health():
    return {"status": "online", "openai": True}

@chat.post("/")
async def chat_handler(data: ChatRequest):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Você é o assistente corporativo MAWDSLEYS."},
                {"role": "user", "content": data.message}
            ],
            temperature=0.4,
            max_tokens=800
        )
        return {"reply": response.choices[0].message["content"]}
    except Exception:
        raise HTTPException(status_code=500, detail="Erro OpenAI")

api.include_router(chat)
app.include_router(api)

print("✅ MAWDSLEYS API pronta com IA REAL (ONLINE)")

# =====================================================
# RUN
# =====================================================
if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000)
