# backend/main.py — MAWDSLEYS API (VERSÃO FINAL ESTÁVEL)

import sys
import os
from pathlib import Path
from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from contextlib import asynccontextmanager
import uvicorn
import openai

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
openai_enabled = False

if OPENAI_API_KEY and OPENAI_API_KEY.startswith("sk-"):
    openai.api_key = OPENAI_API_KEY
    openai_enabled = True
    print("🤖 OpenAI configurada com sucesso")
else:
    print("⚠️ OpenAI NÃO configurada — modo DEMO")

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
    docs_url="/docs",
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
        "docs": "/docs"
    }

@app.get("/health")
async def health():
    return {"status": "ok", "timestamp": datetime.utcnow().isoformat()}

# =====================================================
# ROUTER PRINCIPAL
# =====================================================
api = APIRouter(prefix="/api")

# =====================================================
# AUTH
# =====================================================
auth = APIRouter(prefix="/auth", tags=["Auth"])

class Login(BaseModel):
    email: str
    password: str

@auth.post("/login")
async def login(data: Login):
    return {"token": "fake-token", "email": data.email}

api.include_router(auth)

# =====================================================
# KPIs
# =====================================================
kpis = APIRouter(prefix="/kpis", tags=["KPIs"])

@kpis.get("/")
async def get_kpis():
    return [
        {"id": 1, "name": "Conversão", "current": 78, "target": 85},
        {"id": 2, "name": "Satisfação", "current": 92, "target": 90},
    ]

api.include_router(kpis)

# =====================================================
# MEETINGS
# =====================================================
meetings = APIRouter(prefix="/meetings", tags=["Meetings"])

@meetings.get("/")
async def get_meetings():
    return [
        {"id": 1, "title": "Planejamento", "time": "10:00"},
        {"id": 2, "title": "Review", "time": "14:00"},
    ]

api.include_router(meetings)

# =====================================================
# FOLLOWUPS
# =====================================================
followups = APIRouter(prefix="/followups", tags=["Followups"])

@followups.get("/")
async def get_followups():
    return [
        {"id": 1, "title": "Cliente X"},
        {"id": 2, "title": "Cliente Y"},
    ]

api.include_router(followups)

# =====================================================
# CHAT (IA REAL)
# =====================================================
chat = APIRouter(prefix="/chat", tags=["Chat"])

class ChatRequest(BaseModel):
    message: str
    temperature: Optional[float] = 0.7
    max_tokens: Optional[int] = 800

@chat.get("/health")
async def chat_health():
    return {
        "status": "online",
        "openai": openai_enabled,
        "mode": "ai" if openai_enabled else "demo"
    }

@chat.post("/")
async def chat_handler(data: ChatRequest):
    if not openai_enabled:
        return {
            "reply": f"🤖 Modo DEMO\n\nVocê disse:\n{data.message}",
            "mode": "demo"
        }

    response = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "Você é o assistente corporativo MAWDSLEYS."},
            {"role": "user", "content": data.message},
        ],
        temperature=data.temperature,
        max_tokens=data.max_tokens
    )

    return {
        "reply": response.choices[0].message["content"],
        "mode": "ai"
    }

api.include_router(chat)

# =====================================================
# INCLUDE API
# =====================================================
app.include_router(api)

print("✅ MAWDSLEYS API carregada com sucesso")

# =====================================================
# LOCAL RUN
# =====================================================
if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000)
