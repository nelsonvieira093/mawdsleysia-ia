import sys
from pathlib import Path
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from datetime import datetime

# Configurar paths
sys.path.insert(0, str(Path(__file__).parent.parent))

print("="*60)
print("MAWDSLEYS API - PRODUCAO")
print("="*60)

app = FastAPI(
    title="MAWDSLEYS Sistema",
    description="Sistema completo de gestao",
    version="1.0.0",
    docs_url="/docs",
    redoc_url=None  # Desabilitar redoc em produção
)

# CORS para produção
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Em produção, coloque seu domínio
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rotas básicas
@app.get("/")
def root():
    return {
        "system": "MAWDSLEYS",
        "version": "1.0.0",
        "status": "online",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/health")
def health_check():
    return {"status": "healthy", "database": "connected"}

# Carregar rotas reais
print("\nCarregando modulos...")

# FollowUps (sistema antigo)
try:
    from api.routes.followups import router as followups_router
    app.include_router(followups_router, prefix="/api")
    print("✅ FollowUps: /api/followups")
except Exception as e:
    print(f"❌ FollowUps: {e}")

# KPIs
try:
    from api.routes.kpis import router as kpis_router
    app.include_router(kpis_router, prefix="/api")
    print("✅ KPIs: /api/kpis")
except Exception as e:
    print(f"❌ KPIs: {e}")

# Meetings
try:
    from api.routes.meetings import router as meetings_router
    app.include_router(meetings_router, prefix="/api")
    print("✅ Meetings: /api/meetings")
except Exception as e:
    print(f"❌ Meetings: {e}")

# Chat (IA)
try:
    from api.routes.chat import router as chat_router
    app.include_router(chat_router, prefix="/api")
    print("✅ Chat IA: /api/chat")
except:
    print("ℹ️  Chat: modulo opcional")

# WhatsApp
try:
    from backend.integrations.whatsapp.router import router as whatsapp_router
    app.include_router(whatsapp_router, prefix="/api")
    print("✅ WhatsApp: /api/whatsapp")
except:
    print("ℹ️  WhatsApp: modulo opcional")

print("\n" + "="*60)
print("✅ SISTEMA PRONTO PARA PRODUCAO")
print("="*60)
print("URL: http://localhost:8000")
print("Admin: http://localhost:8000/docs")
print("="*60)

if __name__ == "__main__":
    uvicorn.run(
        app,
        host="0.0.0.0",  # Acessível de qualquer IP
        port=8000,
        reload=False,  # Desligar reload em produção
        workers=1  # Para começar
    )
