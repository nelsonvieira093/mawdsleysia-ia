# backend/main.py — MAWDSLEYS API (OPENAI REAL, SEM DEMO)

import os
import sys
from pathlib import Path
from datetime import datetime
from contextlib import asynccontextmanager

from fastapi import FastAPI, APIRouter, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

# ===============================
# PATHS
# ===============================
BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

print("🚀 Iniciando backend MAWDSLEYS")
print(f"📁 Backend dir: {BASE_DIR}")

# ===============================
# ENV
# ===============================
from dotenv import load_dotenv
load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not OPENAI_API_KEY or len(OPENAI_API_KEY) < 20:
    raise RuntimeError("❌ OPENAI_API_KEY não encontrada ou inválida")

from openai import OpenAI
client = OpenAI(api_key=OPENAI_API_KEY)

print("🤖 OpenAI configurada com sucesso (MODO REAL)")

# ===============================
# LIFESPAN
# ===============================
@asynccontextmanager
async def lifespan(app: FastAPI):
    print("🔄 Inicializando aplicação...")
    yield
    print("👋 Encerrando aplicação...")

# ===============================
# APP
# ===============================
app = FastAPI(
    title="MAWDSLEYS API",
    version="2.0.0",
    docs_url="/docs",
    lifespan=lifespan
)

# ===============================
# CORS
# ===============================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ===============================
# ROOT
# ===============================
@app.get("/")
async def root():
    return {
        "name": "MAWDSLEYS API",
        "status": "online",
        "docs": "/docs"
    }

@app.get("/health")
async def health():
    return {
        "status": "ok",
        "openai": True,
        "timestamp": datetime.utcnow().isoformat()
    }

# ===============================
# API ROUTER
# ===============================
api = APIRouter(prefix="/api")

# ===============================
# AUTH
# ===============================
auth = APIRouter(prefix="/auth", tags=["Auth"])

class Login(BaseModel):
    email: str
    password: str

@auth.post("/login")
async def login(data: Login):
    return {
        "token": "fake-token",
        "email": data.email
    }

api.include_router(auth)

# ===============================
# KPIs
# ===============================
kpis = APIRouter(prefix="/kpis", tags=["KPIs"])

@kpis.get("/")
async def get_kpis():
    return [
        {"id": 1, "name": "Conversão", "current": 78, "target": 85},
        {"id": 2, "name": "Satisfação", "current": 92, "target": 90},
    ]

api.include_router(kpis)

# ===============================
# MEETINGS
# ===============================
meetings = APIRouter(prefix="/meetings", tags=["Meetings"])

@meetings.get("/")
async def get_meetings():
    return [
        {"id": 1, "title": "Planejamento", "time": "10:00"},
        {"id": 2, "title": "Review", "time": "14:00"},
    ]

api.include_router(meetings)

# ===============================
# FOLLOWUPS
# ===============================
followups = APIRouter(prefix="/followups", tags=["Followups"])

@followups.get("/")
async def get_followups():
    return [
        {"id": 1, "title": "Cliente X"},
        {"id": 2, "title": "Cliente Y"},
    ]

api.include_router(followups)

# ===============================
# CHAT — OPENAI REAL (SEM DEMO)
# ===============================
chat = APIRouter(prefix="/chat", tags=["Chat"])

class ChatRequest(BaseModel):
    message: str

@chat.get("/health")
async def chat_health():
    return {
        "status": "online",
        "openai": True,
        "mode": "ai"
    }

@chat.post("/")
async def chat_handler(data: ChatRequest):
    try:
        prompt = f"""
Você é o assistente corporativo MAWDSLEYS.
Seja profissional, claro e objetivo.

Usuário:
{data.message}
"""

        response = client.responses.create(
            model="gpt-4.1-mini",
            input=prompt
        )

        return {
            "reply": response.output_text,
            "model": "gpt-4.1-mini",
            "mode": "ai",
            "timestamp": datetime.utcnow().isoformat()
        }

    except Exception as e:
        print("❌ Erro OpenAI:", e)
        raise HTTPException(
            status_code=500,
            detail="Erro ao processar requisição com OpenAI"
        )

api.include_router(chat)

# ===============================
# INCLUDE API
# ===============================
app.include_router(api)

print("✅ MAWDSLEYS API carregada com OpenAI REAL (sem DEMO)")

# ===============================
# LOCAL RUN
# ===============================
if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000
    )
